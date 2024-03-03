from sqlalchemy import text
from website import db

# Returns a result set of companies in sectors followed by the user ordered by most to least followed
def recommend_specific(user_id):

    # Get the sectors of companies followed by the user
    qrytext = text("SELECT DISTINCT companies.sector_id FROM companies, follows WHERE companies.stock_ticker = follows.stock_ticker AND follows.user_id = (:user_id)")
    qry = qrytext.bindparams(user_id = user_id)
    sectors = db.session.execute(qry)
    row = sectors.fetchone()

    # Check if any sectors are returned
    if row:
        # Add the sector ids to an array and find the number of ids
        sector_ids = [row.sector_id]
        for row in sectors:
            sector_ids.append(row.sector_id)
        length = len(sector_ids)

        # Create the query based on the number of ids
        query_start = "SELECT companies.stock_ticker, COUNT(follows.stock_ticker) AS count FROM companies LEFT JOIN follows ON companies.stock_ticker = follows.stock_ticker WHERE companies.sector_id IN ("
        query_middle = ""
        for s_id in sector_ids:
            query_middle = query_middle + str(s_id) + ","
        query_end = str(sector_ids[length-1]) + ") GROUP BY companies.stock_ticker ORDER BY count DESC"
        final_query = query_start + query_middle + query_end

        # Execute the query
        companies = db.session.execute(text(final_query))
        return companies
    recommend_general()

# Returns a result set of all companies ordered by most to least followed
def recommend_general():

    qry = text("SELECT companies.stock_ticker, COUNT(follows.stock_ticker) AS count FROM companies LEFT JOIN follows ON companies.stock_ticker = follows.stock_ticker GROUP BY companies.stock_ticker ORDER BY count DESC;")
    companies = db.session.execute(qry)

    return companies
