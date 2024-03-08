from sqlalchemy import text
from website import db

def recommend_general():
    """
    Retrieves the top 5 companies based on the number of followers.

    Returns:
        companies: A result set containing the stock ticker and count of followers for each company.
    """
    qry = text("""
    SELECT companies.stock_ticker, COUNT(follows.stock_ticker) AS count 
    FROM companies 
    LEFT JOIN follows ON companies.stock_ticker = follows.stock_ticker 
    GROUP BY companies.stock_ticker 
    ORDER BY count DESC 
    LIMIT 5;
    """)
    companies = db.session.execute(qry)
    return companies

def recommend_specific(user_id):
    """
    Recommends specific companies to a user based on the sectors of companies they follow.

    Args:
        user_id (int): The ID of the user.

    Returns:
        companies (ResultProxy): A ResultProxy object containing the recommended companies.

    Raises:
        None

    """
    # Get the sectors of companies followed by the user
    qrytext = text("SELECT DISTINCT companies.sector_id FROM companies, follows WHERE companies.stock_ticker = follows.stock_ticker AND follows.user_id = (:user_id)")
    qry = qrytext.bindparams(user_id = user_id)
    sectors = db.session.execute(qry)

    # Check if any sectors are returned
    if int(sectors.rowcount) > 0:
        # Add the sector ids to an array and find the number of ids
        sector_ids = [row.sector_id for row in sectors]

        # Create the query based on the number of ids

        subquery = "SELECT stock_ticker FROM follows WHERE user_id = " + str(user_id)

        # Create the main query
        final_query = f"""
        SELECT DISTINCT companies.stock_ticker, COUNT(follows.stock_ticker) AS count 
        FROM companies 
        LEFT JOIN follows ON companies.stock_ticker = follows.stock_ticker 
        WHERE companies.sector_id IN ({','.join(map(str, sector_ids))}) 
        AND companies.stock_ticker NOT IN ({subquery}) 
        GROUP BY companies.stock_ticker 
        ORDER BY count DESC
        """

        # Execute the query
        companies = db.session.execute(text(final_query))

        # Check if at least two companies are returned
        if int(companies.rowcount) > 1:
            print("Specific companies returned")
            return companies

    print("General companies returned")
    return recommend_general()
