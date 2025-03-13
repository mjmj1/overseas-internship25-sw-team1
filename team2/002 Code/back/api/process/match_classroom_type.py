def match_classroom_type(df_final, offer):
    offer['Category'] = offer['Category'].str.lower()
    df_final['Type'] = df_final['Type'].str.lower()
    df_final['Type'] = df_final.apply(lambda x: 'tutorial' if x['Type'] == 'etc' else x['Type'], axis=1)
    return df_final, offer