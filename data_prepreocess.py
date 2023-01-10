import pandas as pd


categories_mapping_chase = {
    "Food & Drink": "Food & Drink",
    "Shopping": "Shopping",
    "Groceries": "Grocery",
    "Gas": "Gas/Automotive",
    "Entertainment": "Entertainment",
    "Travel": "Travel",
    "Home": "Home"
    
}

categories_mapping_co = {
    "Dining": "Food & Drink",
    "Merchandise": "Shopping",
    "Phone/Cable": "Entertainment",
    "Internet": "Entertainment",
    "Gas/Automotive": "Gas/Automotive",
    "Entertainment": "Entertainment",
    "Other Travel": "Travel",
    "Airfare": "Travel",
    "Lodging": "Travel"
}


card_info_col = 'card_info'

chase_prime_path = '/Users/M255032/lufei-wang-local/personal/personal-finance-backend/server/raw_data/chase_prime.csv'
chase_sb_path = '/Users/M255032/lufei-wang-local/personal/personal-finance-backend/server/raw_data/chase_sb.csv'
co_path = '/Users/M255032/lufei-wang-local/personal/personal-finance-backend/server/raw_data/co.csv'

df_chase_prime = pd.read_csv(chase_prime_path)
df_chase_sb = pd.read_csv(chase_sb_path)
df_co = pd.read_csv(co_path)

df_chase_prime[card_info_col] = 'chase_prime'
df_chase_sb[card_info_col] = "chase_starbucks"
df_co[card_info_col] = "capital_one"

df_chase = pd.concat([df_chase_prime, df_chase_sb])

def preprocess_chase_data(df_chase, categories_mapping):
    df_chase = df_chase[df_chase.Type != 'Payment'].copy()
    df_chase['Transaction Date'] = df_chase['Transaction Date'].apply(lambda x: f"{x[-4:]}-{x[0:2]}-{x[3:5]}")

    df_chase = df_chase.rename(columns = {
                                        "Transaction Date": "date",
                                        "Description": "name",
                                        "Amount": "amount",
                                        "Category": "category"
                                        })

    df_chase = df_chase[["date", "name", "amount", "category", "card_info"]].copy()
    df_chase['category_cleaned'] = df_chase['category'].apply(lambda x: categories_mapping.get(x, 'Others'))

    return df_chase


def preprocess_co_data(df_co, categories_mapping):
    df_co = df_co[df_co.Category != 'Payment/Credit' ].copy()
    df_co['Amount'] = df_co.Debit * -1
    df_co.loc[df_co.Amount.isnull(), 'Amount'] = df_co.Credit
    df_co = df_co.rename(columns={
                                    "Transaction Date": "date",
                                    "Description": "name",
                                    "Category": "category",
                                    "Amount": "amount",
                                    "card_info": "card_info"
                                })
    df_co = df_co[["date", "name", "amount", "category", "card_info"]].copy()
    df_co['category_cleaned'] = df_co['category'].apply(lambda x: categories_mapping.get(x, 'Others'))

    return df_co


def preprocess_and_combine(df_chase=df_chase, df_co=df_co):
    df_chase = preprocess_chase_data(df_chase, categories_mapping_chase)
    df_co = preprocess_co_data(df_co, categories_mapping_co)
    df_all = pd.concat([df_chase, df_co])
    df_all = df_all.sort_values(by='date', ascending=False)
    df_all.to_csv('/Users/M255032/lufei-wang-local/personal/personal-finance-backend/data/transactions_all.csv')
    return df_all