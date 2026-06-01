def build_fact_sheet(df: pd.DataFrame, selected_process: str):
    process_col = "Industrial process"
    unit_op_col = "Unit operation"
    production_col = "Annual production in 2022\n(based on FU)"
    elec_col = "SEC \nelectricity"
    fuel_col = "SEC \nfuels"
    steam_col = "SEC \nfuels or electricity for steam or steam from CHP"

    fact_df = df.copy()
    fact_df[process_col] = clean_category(fact_df[process_col])
    fact_df[unit_op_col] = clean_category(fact_df[unit_op_col])

    for col in [production_col, elec_col, fuel_col, steam_col]:
        fact_df[col] = pd.to_numeric(fact_df[col], errors="coerce")

    selected_df = fact_df[fact_df[process_col] == selected_process].copy()

    if selected_df.empty:
        return None

    production_values = (
        selected_df[production_col]
        .dropna()
        .loc[lambda s: s != 0]
        .unique()
    )
    annual_production = production_values[0] if len(production_values) > 0 else 0

    sec_electricity = selected_df[elec_col].fillna(0).sum()
    sec_fuels = selected_df[fuel_col].fillna(0).sum()
    sec_steam = selected_df[steam_col].fillna(0).sum()

    detail_df = selected_df[
        [unit_op_col, elec_col, fuel_col, steam_col]
    ].rename(columns={
        unit_op_col: "Unit Operations",
        elec_col: "SEC Electricity",
        fuel_col: "SEC Fuels",
        steam_col: "SEC Steam"
    })

    return {
        "Annual Production": annual_production,
        "SEC Electricity": sec_electricity,
        "SEC Fuels": sec_fuels,
        "SEC Steam": sec_steam,
        "Rows": selected_df.shape[0],
        "Details": detail_df
    }
