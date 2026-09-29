# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.utils import flt, cint, nowdate, getdate, formatdate, date_diff
from frappe.utils.data import get_first_day, get_last_day, add_days, add_years
from frappe.desk.form.linked_with import get_linked_doctypes, get_linked_docs
from frappe.model.naming import getseries
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import add_days, get_datetime_str
import logging
from datetime import datetime
import calendar


# ============================================================================
# DATE UTILITY FUNCTIONS
# ============================================================================

@frappe.whitelist()
def get_date_diff(start_date, end_date):
    """Get the difference between two dates in days (inclusive)."""
    if not start_date or not end_date:
        return 0
    return frappe.utils.data.date_diff(end_date, start_date) + 1


def get_year_start_date(date):
    """Get the start date of the year for a given date."""
    return str(date)[0:4] + "-01-01"


def get_year_end_date(date):
    """Get the end date of the year for a given date."""
    return str(date)[0:4] + "-12-31"


def nvl(val1, val2):
    """Return val1 if it exists, otherwise val2."""
    return val1 if val1 else val2


# ============================================================================
# DATE VALIDATION FUNCTIONS
# ============================================================================

def check_future_date(date):
    """Check if a date is in the future and throw an error if so."""
    if not date:
        frappe.throw(_("Date Argument Missing"))
    if getdate(date) > getdate(nowdate()):
        frappe.throw(_("Posting for Future Date is not Permitted"))


def check_account_frozen(posting_date):
    """Check if the account is frozen for the given posting date."""
    acc_frozen_upto = frappe.db.get_value('Accounts Settings', None, 'acc_frozen_upto')
    if acc_frozen_upto:
        frozen_accounts_modifier = frappe.db.get_value('Accounts Settings', None, 'frozen_accounts_modifier')
        if getdate(posting_date) <= getdate(acc_frozen_upto) \
                and frozen_accounts_modifier not in frappe.get_roles():
            frappe.throw(_("You are not authorized to add or update entries before {0}").format(
                formatdate(acc_frozen_upto)))


# ============================================================================
# BRANCH/COST CENTER FUNCTIONS
# ============================================================================

def get_branch_cc(branch):
    """Get cost center from branch."""
    if not branch:
        frappe.throw(_("No Branch Argument Found"))
    return frappe.get_doc("Branch", branch).cost_center


@frappe.whitelist()
def get_cc_warehouse(branch):
    """Get cost center and warehouse from branch."""
    cc = get_branch_cc(branch)
    return {"cc": cc, "wh": None}


@frappe.whitelist()
def get_branch_warehouse(branch):
    """Get warehouse from branch."""
    cc = get_branch_cc(branch)
    wh = frappe.db.get_value("Cost Center", cc, "warehouse")
    if not wh:
        frappe.throw(_("No warehouse linked with your branch or cost center"))
    return wh


@frappe.whitelist()
def get_branch_from_cost_center(cost_center):
    """Get branch from cost center."""
    return frappe.db.get_value("Branch", {"cost_center": cost_center, "disabled": 0}, "name")


def get_cc_customer(cc):
    """Get customer from cost center."""
    customer = frappe.db.get_value("Customer", {"cost_center": cc}, "name")
    if not customer:
        frappe.throw(_("No Customer found for the Cost Center"))
    return customer


# ============================================================================
# USER/EMPLOYEE FUNCTIONS
# ============================================================================

@frappe.whitelist()
def get_user_info(user=None, employee=None, cost_center=None, branch=None):
    """
    Get user information including cost center, branch, warehouse, and approver.
    
    Can be called with either user, employee, cost_center, or branch.
    """
    info = {}
    employee_types = ["Employee", "DES Employee", "Muster Roll Employee", "GEP Employee"]
    
    def get_employee_info(emp_name):
        """Helper to get employee info from various employee doctypes."""
        for doctype in employee_types:
            if frappe.db.exists(doctype, {"name": emp_name}):
                cc = frappe.db.get_value(doctype, {"name": emp_name}, "cost_center")
                br = frappe.db.get_value(doctype, {"name": emp_name}, "branch")
                if cc and br:
                    return cc, br
        return None, None
    
    if employee:
        cost_center, branch = get_employee_info(employee)
    elif user:
        for doctype in employee_types:
            if frappe.db.exists(doctype, {"user_id": user}):
                cost_center = frappe.db.get_value(doctype, {"user_id": user}, "cost_center")
                branch = frappe.db.get_value(doctype, {"user_id": user}, "branch")
                if cost_center and branch:
                    break
    elif branch:
        cost_center = frappe.db.get_value("Branch", branch, "cost_center")
    
    if cost_center:
        warehouse = frappe.db.get_value("Cost Center", cost_center, "warehouse")
        approver = frappe.db.get_value("Approver Item", {"cost_center": cost_center}, "approver")
        info.update({
            'cost_center': cost_center,
            'branch': branch,
            'warehouse': warehouse,
            'approver': approver
        })
    
    return info


def get_officiating_employee(employee):
    """Get the officiating employee for a given employee."""
    if not employee:
        frappe.throw(_("Employee is Mandatory"))
    
    qry = """
        SELECT officiate FROM `tabOfficiating Employee`
        WHERE docstatus = 1 AND revoked != 1
        AND %(today)s BETWEEN from_date AND to_date
        AND employee = %(employee)s
        ORDER BY creation DESC LIMIT 1
    """
    
    officiate = frappe.db.sql(qry, {"today": nowdate(), "employee": employee}, as_dict=True)
    
    if officiate:
        flag = True
        while flag:
            temp = frappe.db.sql(qry, {"today": nowdate(), "employee": officiate[0].officiate}, as_dict=True)
            if temp:
                officiate = temp
            else:
                flag = False
    return officiate


# ============================================================================
# RECEIPT NUMBER GENERATION
# ============================================================================

def generate_receipt_no(doctype, docname, branch, fiscal_year):
    """Generate and set receipt number for a document."""
    if doctype and docname:
        abbr = frappe.db.get_value("Branch", branch, "abbr")
        if not abbr:
            frappe.throw(_("Set Branch Abbreviation in Branch Master Record"))
        prefix = f"NRDCL/{abbr}/{fiscal_year}/"
        current = getseries(prefix, 4)
        doc = frappe.get_doc(doctype, docname)
        doc.db_set("money_receipt_no", current)
        doc.db_set("money_receipt_prefix", prefix)


# ============================================================================
# BUDGET FUNCTIONS
# ============================================================================

def check_budget_available(cost_center, budget_account, transaction_date, amount, project=None):
    """
    Check budget availability for a given cost center and account.
    Throws an error if budget is insufficient.
    """
    consumed = committed = None
    fiscal_year = str(transaction_date)[0:4]
    
    if project:
        budget_amount = frappe.db.sql("""
            SELECT b.action_if_annual_budget_exceeded AS action,
                   ba.budget_check, ba.budget_amount, b.deviation
            FROM `tabBudget` b, `tabBudget Cost Center` ba
            WHERE b.docstatus = 1
            AND ba.parent = b.name AND ba.cost_center = %s
            AND b.fiscal_year = %s
            AND b.project = %s
        """, (cost_center, fiscal_year, project), as_dict=True)
        
        if budget_amount:
            committed = frappe.db.sql("""
                SELECT SUM(cb.amount) AS total
                FROM `tabCommitted Budget` cb
                WHERE cb.cost_center = %s AND cb.project = %s
                AND cb.reference_date BETWEEN %s AND %s
            """, (cost_center, project, f"{fiscal_year}-01-01", f"{fiscal_year}-12-31"), as_dict=True)
            
            consumed = frappe.db.sql("""
                SELECT SUM(cb.amount) AS total
                FROM `tabConsumed Budget` cb
                WHERE cb.cost_center = %s AND cb.project = %s
                AND cb.reference_date BETWEEN %s AND %s
            """, (cost_center, project, f"{fiscal_year}-01-01", f"{fiscal_year}-12-31"), as_dict=True)
            
        msg = f"Project: <b>{project}</b>, for Cost Center: <b>{cost_center}</b> level for <b>{fiscal_year}</b>"
    
    else:
        # Handle account-based budget checking
        bud_acc_dtl = frappe.get_doc("Account", budget_account)
        
        if bud_acc_dtl.has_linked_budget == 1:
            budget_account = bud_acc_dtl.linked_budget
        
        # Skip if budget check is disabled
        if bud_acc_dtl.budget_check:
            return
        
        # Handle centralized budget
        if bud_acc_dtl.is_centralized_budget:
            cost_center = bud_acc_dtl.cost_center
        else:
            cc_doc = frappe.get_doc("Cost Center", cost_center)
            if cc_doc.use_budget_from_parent:
                cost_center = cc_doc.parent_cost_center
        
        budget_amount = frappe.db.sql("""
            SELECT b.action_if_annual_budget_exceeded AS action,
                   ba.budget_check, ba.budget_amount, b.deviation
            FROM `tabBudget` b, `tabBudget Account` ba
            WHERE b.docstatus = 1
            AND ba.parent = b.name AND ba.account = %s
            AND b.fiscal_year = %s
            AND b.cost_center = %s
        """, (budget_account, fiscal_year, cost_center), as_dict=True)
        
        if budget_amount:
            committed = frappe.db.sql("""
                SELECT SUM(cb.amount) AS total
                FROM `tabCommitted Budget` cb
                WHERE cb.account = %s AND cb.cost_center = %s
                AND cb.reference_date BETWEEN %s AND %s
            """, (budget_account, cost_center, f"{fiscal_year}-01-01", f"{fiscal_year}-12-31"), as_dict=True)
            
            consumed = frappe.db.sql("""
                SELECT SUM(cb.amount) AS total
                FROM `tabConsumed Budget` cb
                WHERE cb.account = %s AND cb.cost_center = %s
                AND cb.reference_date BETWEEN %s AND %s
            """, (budget_account, cost_center, f"{fiscal_year}-01-01", f"{fiscal_year}-12-31"), as_dict=True)
            
        msg = f"Account: <b>{budget_account}</b> set at <b>{cost_center}</b> level for <b>{fiscal_year}</b>"
    
    if not budget_amount:
        frappe.throw(_("There is no budget allocated for ") + str(msg))
    
    # Check if we should ignore budget limits
    action = budget_amount[0].action
    budget_check = budget_amount[0].budget_check
    if action == "Ignore" or budget_check == "Ignore":
        return
    
    if consumed and committed:
        if flt(consumed[0].total) > flt(committed[0].total):
            committed = consumed
        
        total_consumed = flt(committed[0].total) + flt(amount)
        total_budget = flt(budget_amount[0].budget_amount)
        
        if budget_amount[0].deviation > 0:
            total_budget += flt(budget_amount[0].deviation * budget_amount[0].budget_amount) / 100
        
        if total_consumed > total_budget:
            balance_budget = flt(budget_amount[0].budget_amount) - flt(committed[0].total)
            insufficient = flt(amount) - balance_budget
            frappe.throw(_(
                f"Budget of Nu. {insufficient} insufficient in <b>{msg}</b>. "
                f"Total Budget is Nu. {flt(budget_amount[0].budget_amount)}, "
                f"total Consumed and Committed is Nu. {flt(committed[0].total)}. "
                f"Balance budget is Nu. {balance_budget}."
            ))
    else:
        frappe.throw(_("There is no budget allocated for ") + str(msg))


def check_budget_available_for_reappropiation(cost_center, budget_account, transaction_date, amount):
    """Check budget availability for re-appropriation."""
    budget_against = frappe.db.get_single_value("Accounts Settings", "budget_level")
    if not budget_against:
        frappe.throw(_("Budget Level not set in Accounts Settings"))
    
    fiscal_year = str(transaction_date)[0:4]
    
    if budget_against == "Cost Center":
        cond = f" AND b.budget_against = '{budget_against}' AND b.cost_center = '{cost_center}'"
    else:
        cond = f" AND b.budget_against = '{budget_against}'"
    
    budget_amount = frappe.db.sql(f"""
        SELECT b.action_if_annual_budget_exceeded AS action,
               ba.budget_check, ba.budget_amount, b.deviation
        FROM `tabBudget` b, `tabBudget Account` ba
        WHERE b.docstatus = 1
        AND ba.parent = b.name AND ba.account = '{budget_account}'
        AND b.fiscal_year = '{fiscal_year}' {cond}
    """, as_dict=True)
    
    if budget_amount:
        if budget_against == "Cost Center":
            committed = frappe.db.sql("""
                SELECT SUM(cb.amount) AS total
                FROM `tabCommitted Budget` cb
                WHERE cb.account = %s AND cb.cost_center = %s
                AND cb.po_date BETWEEN %s AND %s
            """, (budget_account, cost_center, f"{fiscal_year}-01-01", f"{fiscal_year}-12-31"), as_dict=True)
            
            consumed = frappe.db.sql("""
                SELECT SUM(cb.amount) AS total
                FROM `tabConsumed Budget` cb
                WHERE cb.account = %s AND cb.cost_center = %s
                AND cb.po_date BETWEEN %s AND %s
            """, (budget_account, cost_center, f"{fiscal_year}-01-01", f"{fiscal_year}-12-31"), as_dict=True)
        else:
            committed = frappe.db.sql("""
                SELECT SUM(cb.amount) AS total
                FROM `tabCommitted Budget` cb
                WHERE cb.account = %s
                AND cb.po_date BETWEEN %s AND %s
            """, (budget_account, f"{fiscal_year}-01-01", f"{fiscal_year}-12-31"), as_dict=True)
            
            consumed = frappe.db.sql("""
                SELECT SUM(cb.amount) AS total
                FROM `tabConsumed Budget` cb
                WHERE cb.account = %s
                AND cb.po_date BETWEEN %s AND %s
            """, (budget_account, f"{fiscal_year}-01-01", f"{fiscal_year}-12-31"), as_dict=True)
        
        if consumed and committed:
            if flt(consumed[0].total) > flt(committed[0].total):
                committed = consumed
            total_consumed = flt(committed[0].total) + flt(amount)
            
            if total_consumed > flt(budget_amount[0].budget_amount):
                frappe.msgprint(_(
                    f"Total Amount consumed: {total_consumed} and Budget Amount: {budget_amount[0].budget_amount}"
                ))
                exceeded = total_consumed - flt(budget_amount[0].budget_amount)
                frappe.throw(_(
                    f"Not enough budget in <b>{budget_account}</b>. "
                    f"The budget is exceeded by <b>{exceeded}</b>"
                ))
    else:
        frappe.throw(_("There is no budget allocated in <b>{}</b>").format(budget_account))


def cancel_budget_entry(reference_type, reference_no):
    """Cancel budget entries for a given reference."""
    for table in ["Consumed Budget", "Commited Budget"]:
        if frappe.db.exists(table, {"reference_type": reference_type, "reference_no": reference_no}):
            doc = frappe.get_doc(table, {"reference_type": reference_type, "reference_no": reference_no})
            doc.cancel()
            frappe.db.sql(
                f"DELETE FROM `tab{table}` WHERE reference_type = %s AND reference_no = %s",
                (reference_type, reference_no)
            )


# ============================================================================
# BUDGET LEDGER PREPARATION FUNCTIONS
# ============================================================================

def prepare_sl(d, args):
    """Prepare a basic stock ledger entry."""
    sl_dict = frappe._dict({
        "item_code": d.pol_type,
        "warehouse": d.warehouse,
        "posting_date": d.posting_date,
        "posting_time": d.posting_time,
        'fiscal_year': get_fiscal_year(d.posting_date, company=d.company)[0],
        "voucher_type": d.doctype,
        "voucher_no": d.name,
        "voucher_detail_no": d.name,
        "actual_qty": 0,
        "stock_uom": d.stock_uom,
        "incoming_rate": 0,
        "company": d.company,
        "batch_no": "",
        "serial_no": "",
        "project": "",
        "is_cancelled": "Yes" if d.docstatus == 2 else "No"
    })
    sl_dict.update(args)
    return sl_dict


def prepare_gl(d, args):
    """Prepare a basic general ledger entry."""
    gl_dict = frappe._dict({
        'company': d.company,
        'posting_date': d.posting_date,
        'fiscal_year': get_fiscal_year(d.posting_date, company=d.company)[0],
        'voucher_type': d.doctype,
        'voucher_no': d.name,
        'remarks': '',
        'debit': 0,
        'credit': 0,
        'debit_in_account_currency': 0,
        'credit_in_account_currency': 0,
        'is_opening': "No",
        'party_type': None,
        'party': None,
        'project': ""
    })
    gl_dict.update(args)
    return gl_dict


# ============================================================================
# DOCUMENT LINK/PERMISSION FUNCTIONS
# ============================================================================

def check_uncancelled_linked_doc(doctype, docname):
    """Check if there are uncancelled documents linked to the given document."""
    linked_doctypes = get_linked_doctypes(doctype)
    linked_docs = get_linked_docs(doctype, docname, linked_doctypes)
    for docs in linked_docs:
        for doc in linked_docs[docs]:
            if doc['docstatus'] < 2:
                frappe.throw(_("There is an uncancelled {0} linked with this document").format(
                    frappe.get_desk_link(docs, doc['name'])
                ))


@frappe.whitelist()
def get_prev_doc(doctype, docname, col_list=""):
    """Get previous document or specific columns from a document."""
    if col_list:
        return frappe.db.get_value(doctype, docname, col_list.split(","), as_dict=1)
    return frappe.get_doc(doctype, docname)


def has_record_permission(doc, user):
    """Check if a user has permission to access a record."""
    if not user:
        user = frappe.session.user
    
    user_roles = frappe.get_roles(user)
    if user == "Administrator" or "System Manager" in user_roles:
        return True
    
    if frappe.db.exists("Employee", {"branch": doc.branch, "user_id": user}):
        return True
    
    result = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
        WHERE e.user_id = %s
        AND ab.employee = e.name
        AND bi.parent = ab.name
        AND bi.branch = %s
    """, (user, doc.branch))
    
    return result[0][0] > 0


# ============================================================================
# PAYROLL/LEAVE FUNCTIONS
# ============================================================================

@frappe.whitelist()
def get_salary_tax(gross_amt):
    """Calculate salary tax based on gross amount."""
    tax_amount = 0
    max_limit = frappe.db.sql("""
        SELECT MAX(b.to_amount)
        FROM `tabIncome Tax Slab` a, `tabTaxable Salary Slab` b
        WHERE NOW() BETWEEN a.effective_from AND IFNULL(a.effective_till, NOW())
        AND b.parent = a.name
    """)
    
    max_amount = flt(max_limit[0][0]) if max_limit and max_limit[0][0] else 0
    
    if not gross_amt or not max_amount:
        return 0
    
    if flt(gross_amt) > flt(max_amount):
        tax_amount = ((flt(gross_amt) - 125000.00) * 0.30) + 20208.00
    else:
        result = frappe.db.sql("""
            SELECT IFNULL(b.tax, 0)
            FROM `tabIncome Tax Slab` a, `tabTaxable Salary Slab` b
            WHERE NOW() BETWEEN a.effective_from AND IFNULL(a.effective_till, NOW())
            AND b.parent = a.name
            AND %s BETWEEN IFNULL(b.from_amount, 0) AND IFNULL(b.to_amount, 0)
            LIMIT 1
        """, flt(gross_amt))
        
        if result:
            tax_amount = result[0][0]
    
    return flt(tax_amount)


@frappe.whitelist()
def get_basic_and_gross_pay(employee, effective_date):
    """Get basic and gross pay for an employee."""
    SalaryStructure = frappe.qb.DocType("Salary Structure")
    SalaryDetail = frappe.qb.DocType("Salary Detail")
    
    query = (
        frappe.qb.from_(SalaryStructure)
        .join(SalaryDetail)
        .on(SalaryStructure.name == SalaryDetail.parent)
        .select(
            SalaryStructure.net_pay,
            SalaryStructure.total_earning,
            SalaryDetail.amount.as_("basic_pay")
        )
        .where(
            (SalaryStructure.is_active == "Yes")
            & (SalaryStructure.employee == employee)
            & (SalaryDetail.salary_component == "Basic Salary")
        )
    )
    
    results = query.run(as_dict=True)
    return results[0] if results else None


@frappe.whitelist()
def get_payroll_settings(employee=None):
    """Get payroll settings for an employee."""
    settings = {}
    if employee:
        settings = frappe.db.sql("""
            SELECT
                e.employee_group,
                e.grade,
                d.sws_contribution,
                d.gis,
                g.health_contribution,
                g.employee_pf,
                g.employer_pf
            FROM `tabEmployee` e
            INNER JOIN `tabEmployee Group` g ON g.name = e.employee_group
            INNER JOIN `tabEmployee Grade` d ON d.name = e.grade
            WHERE e.name = %s
        """, employee, as_dict=True)
    
    return settings[0] if settings else frappe._dict()


# ============================================================================
# SETTINGS UTILITY FUNCTIONS
# ============================================================================

def get_settings_value(setting_dt, company, field_name):
    """Get a settings value for a company."""
    value = frappe.db.sql(
        f"SELECT {field_name} FROM `tab{setting_dt}` WHERE company = %s",
        company
    )
    return value[0][0] if value and value[0] else None


def round5(x, prec=1, base=0.5):
    """Round to the nearest 5 with specified precision."""
    return round(base * round(flt(x) / base), prec)


# ============================================================================
# PRODUCTION UTILITY FUNCTIONS
# ============================================================================

def get_production_groups(group):
    """Get production groups items."""
    if not group:
        frappe.throw(_("Invalid Production Group"))
    
    groups = []
    for a in frappe.db.sql(
        "SELECT item_code FROM `tabProduction Group Item` WHERE parent = %s",
        group,
        as_dict=1
    ):
        groups.append(str(a.item_code))
    return groups


# ============================================================================
# EMAIL/SESSION UTILITY FUNCTIONS
# ============================================================================

def sendmail(recipient, subject, message, sender=None):
    """Send an email."""
    try:
        frappe.sendmail(recipients=recipient, sender=sender, subject=subject, message=message)
    except Exception:
        pass


def send_mail_to_role_branch(branch, role, message, subject=None):
    """Send email to users with a specific role and branch."""
    if not subject:
        subject = "Message from ERP System"
    
    users = frappe.db.sql_list("""
        SELECT DISTINCT a.parent
        FROM `tabHas Role` a
        INNER JOIN tabDefaultValue b ON a.parent = b.parent
        WHERE b.defvalue = %s AND b.defkey = 'Branch' AND a.role = %s
    """, (branch, role))
    
    try:
        frappe.sendmail(recipients=users, subject=subject, message=message)
    except Exception:
        pass


@frappe.whitelist()
def kick_users():
    """Kick all users out of the system."""
    from frappe.sessions import clear_all_sessions
    clear_all_sessions()
    frappe.msgprint(_("Kicked All Out!"))


# ============================================================================
# MONTH DETAILS UTILITY
# ============================================================================

@frappe.whitelist()
def get_month_details(year, month):
    """Get month details for a fiscal year."""
    ysd = frappe.db.get_value("Fiscal Year", year, "year_start_date")
    if not ysd:
        frappe.throw(_("Fiscal Year {0} not found").format(year))
    
    from dateutil.relativedelta import relativedelta
    import datetime as dt
    
    diff_mnt = cint(month) - cint(ysd.month)
    if diff_mnt < 0:
        diff_mnt = 12 - int(ysd.month) + cint(month)
    
    msd = ysd + relativedelta(months=diff_mnt)  # month start date
    month_days = cint(calendar.monthrange(cint(msd.year), cint(month))[1])  # days in month
    med = dt.date(msd.year, cint(month), month_days)  # month end date
    
    return frappe._dict({
        'year': msd.year,
        'month_start_date': msd,
        'month_end_date': med,
        'month_days': month_days
    })


# ============================================================================
# LEAVE ALLOCATION FUNCTIONS
# ============================================================================

def post_leave_credits(today=None):
    """
    Allocate leaves in bulk as per the leave credits defined in Employee Group master.
    
    This method is mainly used for allocating monthly and yearly leave credits automatically.
    """
    # Setup logging
    logging.basicConfig(
        format='%(asctime)s|%(name)s|%(levelname)s|%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)
    
    today = getdate(today) if today else getdate(nowdate())
    f_date = get_first_day(add_days(today, -today.day))
    t_date = get_last_day(f_date)
    
    elist = frappe.db.sql("""
        SELECT
            t1.name, t1.employee_name, t1.date_of_joining,
            CASE
                WHEN DAY(t1.date_of_joining) > 1 AND DAY(t1.date_of_joining) <= 15
                THEN TIMESTAMPDIFF(MONTH, t1.date_of_joining, %s) + 1
                ELSE TIMESTAMPDIFF(MONTH, t1.date_of_joining, %s)
            END AS no_of_months,
            t2.leave_type, t2.credits_per_month, t2.credits_per_year,
            t3.is_carry_forward
        FROM `tabEmployee` t1
        INNER JOIN `tabEmployee Group Item` t2 ON t1.employee_group = t2.parent
        INNER JOIN `tabLeave Type` t3 ON t3.name = t2.leave_type
        WHERE t1.status = 'Active'
        AND t1.date_of_joining <= %s
        AND (t2.credits_per_month > 0 OR t2.credits_per_year > 0)
        AND NOT EXISTS (
            SELECT 1
            FROM `tabLeave Allocation` t4
            WHERE t4.employee = t1.name
            AND t4.docstatus != 2
            AND t4.from_date = %s
            AND t4.to_date = %s
            AND t4.leave_type = t3.name
        )
        ORDER BY t1.name, t2.leave_type
    """, (str(today), str(today), str(today), f_date, t_date), as_dict=1)
    
    counter = 0
    for e in elist:
        counter += 1
        
        if flt(e.no_of_months) <= 0:
            logger.error(f"NOT QUALIFIED|{counter}|{e.name}|{e.employee_name}|{e.leave_type}")
            continue
        
        credits_per_month = 0
        start_date = get_first_day(today)
        end_date = get_last_day(start_date)
        
        # Monthly credits for Earned Leave
        if flt(e.credits_per_month) > 0 and e.leave_type == "Earned Leave":
            credits_per_month, start_date, end_date = _calculate_earned_leave_credits(
                e, today, logger, counter
            )
        else:
            start_date = get_first_day(today)
            end_date = get_last_day(start_date)
            credits_per_month = flt(e.credits_per_month) if flt(e.credits_per_month) > 0 else 0
        
        leave_allocation = []
        if credits_per_month > 0:
            leave_allocation.append({
                'from_date': str(start_date),
                'to_date': str(end_date),
                'new_leaves_allocated': flt(credits_per_month)
            })
        
        # Yearly credits
        if flt(e.credits_per_year) > 0:
            start_date = get_year_start_date(today)
            end_date = get_year_end_date(start_date)
            leave_allocation.append({
                'from_date': str(start_date),
                'to_date': str(end_date),
                'new_leaves_allocated': flt(e.credits_per_year)
            })
        
        for la in leave_allocation:
            if not frappe.db.exists("Leave Allocation", {
                "employee": e.name,
                "leave_type": e.leave_type,
                "from_date": la['from_date'],
                "to_date": la['to_date'],
                "docstatus": ("<", 2)
            }):
                try:
                    doc = frappe.new_doc("Leave Allocation")
                    doc.employee = e.name
                    doc.employee_name = e.employee_name
                    doc.leave_type = e.leave_type
                    doc.from_date = la['from_date']
                    doc.to_date = la['to_date']
                    doc.carry_forward = cint(e.is_carry_forward)
                    doc.new_leaves_allocated = flt(la['new_leaves_allocated'])
                    doc.submit()
                    logger.info(f"SUCCESS|{counter}|{e.name}|{e.employee_name}|{e.leave_type}|{flt(la['new_leaves_allocated'])}")
                except Exception as ex:
                    logger.exception(f"FAILED|{counter}|{e.name}|{e.employee_name}|{e.leave_type}|{flt(la['new_leaves_allocated'])}")
            else:
                logger.warning(f"ALREADY ALLOCATED|{counter}|{e.name}|{e.employee_name}|{e.leave_type}|{flt(la['new_leaves_allocated'])}")


def _calculate_earned_leave_credits(e, today, logger, counter):
    """Helper function to calculate earned leave credits."""
    start_date = get_first_day(add_days(today, -20))
    end_date = get_last_day(start_date)
    
    emplist = frappe.db.sql("""
        SELECT a.employee, a.employee_name, a.from_date, a.to_date
        FROM `tabLeave Application` a
        INNER JOIN `tabLeave Type` b ON a.leave_type = b.name
        INNER JOIN `tabLeave Type Item` c ON b.name = c.parent
        WHERE (a.from_date BETWEEN %s AND %s OR a.to_date BETWEEN %s AND %s OR %s BETWEEN a.from_date AND a.to_date)
        AND a.employee = %s
        AND c.leave_type = 'Earned Leave'
        AND a.docstatus = 1
        UNION
        SELECT employee, employee_name, from_date, to_date
        FROM `tabEmployee Disciplinary Record`
        WHERE (from_date BETWEEN %s AND %s OR to_date BETWEEN %s AND %s OR %s BETWEEN from_date AND to_date)
        AND employee = %s
        AND not_guilty_or_acquitted = 0
        AND docstatus = 1
    """, (
        str(start_date), str(end_date), str(start_date), str(end_date), str(today), e.name,
        str(start_date), str(end_date), str(start_date), str(end_date), str(today), e.name
    ), as_dict=True)
    
    if emplist:
        total_days_in_month = date_diff(end_date, start_date)
        leave_allocation_per_day = flt(e.credits_per_month / total_days_in_month)
        total_leaves = 0
        
        for l in emplist:
            if l.from_date >= start_date and l.to_date <= end_date:
                total_leaves += date_diff(l.to_date, l.from_date)
            elif l.from_date < start_date and l.to_date < end_date:
                total_leaves += date_diff(l.to_date, start_date)
            elif l.from_date > start_date and l.to_date > end_date:
                total_leaves += date_diff(end_date, l.from_date)
        
        total_working_days = total_days_in_month - total_leaves
        credits_per_month = flt(total_working_days) * flt(leave_allocation_per_day)
        logger.info(f"{e.name}|{e.employee_name}|{e.leave_type}|{flt(total_working_days)}|{flt(credits_per_month)}|{flt(leave_allocation_per_day)}")
        return credits_per_month, start_date, end_date
    else:
        return flt(e.credits_per_month), start_date, end_date


def adjust_el():
    """Adjust earned leave allocation when employee leaves fall within the month."""
    logging.basicConfig(
        format='%(asctime)s|%(name)s|%(levelname)s|%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)
    
    emplist = frappe.db.sql("""
        SELECT employee, employee_name, from_date, to_date, total_leave_days
        FROM `tabLeave Application`
        WHERE (
            from_date BETWEEN DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%Y-%m-01')
            AND LAST_DAY(CURDATE() - INTERVAL 1 MONTH)
            OR to_date BETWEEN DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%Y-%m-01')
            AND LAST_DAY(CURDATE() - INTERVAL 1 MONTH)
        )
        AND docstatus = 1
        AND EXISTS (
            SELECT 1 FROM `tabLeave Type` WHERE dont_allocate_el = 1
        )
        ORDER BY employee
    """, as_dict=1)
    
    cur_date = getdate(nowdate())
    first = datetime.date(day=1, month=cur_date.month, year=cur_date.year)
    end_date = first - datetime.timedelta(days=1)
    start_date = datetime.date(day=1, month=end_date.month, year=end_date.year)
    total_days = calendar.monthrange(start_date.year, start_date.month)[1]
    
    for l in emplist:
        no_of_leave_days = _calculate_leave_days(l, start_date, end_date)
        allocated_el = flt(0.08 * (total_days - no_of_leave_days))
        
        is_carry_forward = frappe.get_value("Leave Type", "Earned Leave", "is_carry_forward")
        
        if frappe.db.exists("Leave Allocation", {
            "employee": l.employee,
            "leave_type": "Earned Leave",
            "from_date": start_date,
            "to_date": end_date,
            "docstatus": ("<", 2)
        }):
            doc = frappe.get_doc("Leave Allocation", {
                "employee": l.employee,
                "leave_type": "Earned Leave",
                "from_date": start_date,
                "to_date": end_date,
                "docstatus": ("<", 2)
            })
            total_leaves = flt(doc.total_leaves_allocated) - flt(doc.new_leaves_allocated) + flt(allocated_el)
            doc.db_set("new_leaves_allocated", allocated_el)
            doc.db_set("total_leaves_allocated", total_leaves)
            logger.info(f"SUCCESS|{l.name}|{l.employee_name}|Modified Existing allocation|{flt(allocated_el)}")
        else:
            doc = frappe.new_doc("Leave Allocation")
            doc.employee = l.employee
            doc.employee_name = l.employee_name
            doc.leave_type = "Earned Leave"
            doc.from_date = start_date
            doc.to_date = end_date
            doc.carry_forward = cint(is_carry_forward)
            doc.new_leaves_allocated = flt(allocated_el)
            doc.submit()
            logger.info(f"SUCCESS|{l.name}|{l.employee_name}|Created new allocation|{flt(allocated_el)}")


def _calculate_leave_days(l, start_date, end_date):
    """Helper function to calculate leave days for adjustment."""
    if l.from_date >= start_date and l.to_date <= end_date:
        return l.total_leave_days
    elif l.from_date < start_date and l.to_date < end_date:
        first_date = datetime.strptime(str(l.to_date), "%Y-%m-%d")
        second_date = datetime.strptime(str(start_date), "%Y-%m-%d")
        return (first_date - second_date).days
    elif l.from_date > start_date and l.to_date > end_date:
        first_date = datetime.strptime(str(end_date), "%Y-%m-%d")
        second_date = datetime.strptime(str(l.from_date), "%Y-%m-%d")
        return (first_date - second_date).days
    return 0


# ============================================================================
# LEGACY LEAVE POSTING FUNCTIONS (Kept for backward compatibility)
# ============================================================================

def post_casual_leaves():
    """Post casual leave on the first day of every year."""
    date = getdate(frappe.utils.nowdate())
    if not (date.month == 1 and date.day == 1):
        return 0
    
    start = get_year_start_date(date)
    end = get_year_end_date(date)
    
    employees = frappe.db.sql(
        "SELECT name, employee_name FROM `tabEmployee` WHERE status = 'Active'",
        as_dict=True
    )
    
    for e in employees:
        la = frappe.new_doc("Leave Allocation")
        la.employee = e.name
        la.employee_name = e.employee_name
        la.leave_type = "Casual Leave"
        la.from_date = str(start)
        la.to_date = str(end)
        la.carry_forward = 0
        la.new_leaves_allocated = 10
        la.submit()


def post_earned_leaves():
    """Post earned leave on the first day of every month."""
    if getdate(frappe.utils.nowdate()) != getdate(get_first_day(frappe.utils.nowdate())):
        return 0
    
    date = add_days(frappe.utils.nowdate(), -20)
    start = get_first_day(date)
    end = get_last_day(date)
    
    employees = frappe.db.sql(
        "SELECT name, employee_name, date_of_joining FROM `tabEmployee` WHERE status = 'Active'",
        as_dict=True
    )
    
    for e in employees:
        if cint(date_diff(end, getdate(e.date_of_joining))) > 14:
            la = frappe.new_doc("Leave Allocation")
            la.employee = e.name
            la.employee_name = e.employee_name
            la.leave_type = "Earned Leave"
            la.from_date = str(start)
            la.to_date = str(end)
            la.carry_forward = 1
            la.new_leaves_allocated = 2.5
            la.submit()


# ============================================================================
# DISCIPLINARY RECORD UPDATE FUNCTION
# ============================================================================

def update_suspension_record():
    """Update employee suspension record when suspension ends."""
    data = frappe.db.sql("""
        SELECT employee, increment_month, promotion_month
        FROM `tabEmployee Disciplinary Record`
        WHERE docstatus = 1
        AND not_quilty_or_acquitted = 0
        AND DATE_ADD(to_date, INTERVAL 1 DAY) = %s
    """, nowdate())
    
    for d in data:
        emp = frappe.get_doc("Employee", d[0])
        emp.employment_status = "In Service"
        emp.increment_and_promotion_cycle = d[1]
        emp.promotion_cycle = d[2]
        emp.save()

# ============================================================================
# EXCHANGE RATE 
# ============================================================================

@frappe.whitelist()
def get_exchange_rate(from_currency, to_currency, transaction_date=None, args=None):
	if not (from_currency and to_currency):
		# manqala 19/09/2016: Should this be an empty return or should it throw and exception?
		return
	if from_currency == to_currency:
		return 1

	if not transaction_date:
		transaction_date = nowdate()
	currency_settings = frappe.get_doc("Accounts Settings").as_dict()
	allow_stale_rates = currency_settings.get("allow_stale")

	filters = [
		["date", "<=", get_datetime_str(transaction_date)],
		["from_currency", "=", from_currency],
		["to_currency", "=", to_currency],
	]

	if args == "for_buying":
		filters.append(["for_buying", "=", "1"])
	elif args == "for_selling":
		filters.append(["for_selling", "=", "1"])

	if not allow_stale_rates:
		stale_days = currency_settings.get("stale_days")
		checkpoint_date = add_days(transaction_date, -stale_days)
		filters.append(["date", ">", get_datetime_str(checkpoint_date)])

	# cksgb 19/09/2016: get last entry in Currency Exchange with from_currency and to_currency.
	entries = frappe.get_all(
		"Currency Exchange", fields=["exchange_rate"], filters=filters, order_by="date desc", limit=1
	)
	if entries:
		return flt(entries[0].exchange_rate)

	try:
		cache = frappe.cache()
		key = "currency_exchange_rate_{0}:{1}:{2}".format(transaction_date, from_currency, to_currency)
		value = cache.get(key)

		if not value:
			import requests

			settings = frappe.get_cached_doc("Currency Exchange Settings")
			req_params = {
				"transaction_date": transaction_date,
				"from_currency": from_currency,
				"to_currency": to_currency,
			}
			params = {}
			for row in settings.req_params:
				params[row.key] = format_ces_api(row.value, req_params)
			response = requests.get(format_ces_api(settings.api_endpoint, req_params), params=params)
			# expire in 6 hours
			response.raise_for_status()
			value = response.json()
			for res_key in settings.result_key:
				value = value[format_ces_api(str(res_key.key), req_params)]
			cache.setex(name=key, time=21600, value=flt(value))
		return flt(value)
	except Exception:
		frappe.log_error("Unable to fetch exchange rate")
		frappe.msgprint(
			_(
				"Unable to find exchange rate for {0} to {1} for key date {2}. Please create a Currency Exchange record manually"
			).format(from_currency, to_currency, transaction_date)
		)
		return 0.0
    
def format_ces_api(data, param):
    return data.format(
        transaction_date=param.get("transaction_date"),
        to_currency=param.get("to_currency"),
        from_currency=param.get("from_currency"),
    )