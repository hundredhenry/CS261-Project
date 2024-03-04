from sqlalchemy import text
from .website import db

# Returns a result set of companies in sectors followed by the user ordered by most to least followed
def recommend_specific(userID):

    # Get the sectors of companies followed by the user
    qrytext = text("SELECT DISTINCT companies.sectorID FROM companies, follows WHERE companies.stock_ticker = follows.stock_ticker AND follows.userID = (:userID)")
    qry = qrytext.bindparams(userID = userID)
    sectors = db.session.execute(qry)
    row = sectors.fetchone()

    # Check if any sectors are returned
    if row:
        # Add the sector ids to an array and find the number of ids
        sectorids = [row.sectorID]
        for row in sectors:
            sectorids.append(row.sectorID)
        length = len(sectorids)

        # Create the query based on the number of ids
        query_start = "SELECT DISTINCT companies.stock_ticker, COUNT(follows.stock_ticker) AS count FROM companies LEFT JOIN follows ON companies.stock_ticker = follows.stock_ticker WHERE companies.sectorID IN ("
        query_middle = ""
        for id in sectorids:
            query_middle = query_middle + str(id) + ","
        query_end = str(sectorids[length-1]) + ") AND follows.stock_ticker IS NULL OR (follows.stock_ticker IS NOT NULL AND follows.userID <> " + str(userID) + ") GROUP BY companies.stock_ticker ORDER BY count DESC"
        final_query = query_start + query_middle + query_end

        # Execute the query
        companies = db.session.execute(text(final_query))

        return companies
    else:
        recommend_general()


# Returns a result set of all companies ordered by most to least followed
def recommend_general():

    qry = text("SELECT companies.stock_ticker, COUNT(follows.stock_ticker) AS count FROM companies LEFT JOIN follows ON companies.stock_ticker = follows.stock_ticker GROUP BY companies.stock_ticker ORDER BY count DESC;")
    companies = db.session.execute(qry)

    return companies