import datetime


def queryset_fits_vehicle(queryset, product_fitment_table_name, product_table_name, start_year, end_year, make, model, sub_model=None, engines=[]):
    """
    Below filters use rawsql because built in django exists filter is quite slow as it adds unnecessary group bys
    The performance on the filter goes from 100+ seconds to under 1 second
    Culprit was entire SQL turns into a subquery with odd group bys
    """
    make_condition_join = "INNER JOIN django_vehiclefitment_vehiclemake ON django_vehiclefitment_vehiclemake.id = django_vehiclefitment_vehicle.make_id" if not isinstance(make, int) else ""
    make_condition_sql = f"AND django_vehiclefitment_vehiclemake.name = '{make}'" if not isinstance(make, int) else f"AND django_vehiclefitment_vehicle.make_id = {make}"

    model_condition_join = "INNER JOIN django_vehiclefitment_vehiclemodel ON django_vehiclefitment_vehiclemodel.id = django_vehiclefitment_vehicle.model_id" if not isinstance(model, int) else ""
    model_condition_sql = f"AND django_vehiclefitment_vehiclemodel.name = '{model}'" if not isinstance(model, int) else f"AND django_vehiclefitment_vehicle.model_id = {model}"

    sub_model_condition_join = ""
    sub_model_condition_sql = ""

    engine_condition_join = ""
    engine_condition_sql = ""

    if sub_model:
        sub_model_condition_join = "INNER JOIN django_vehiclefitment_vehiclesubmodel ON django_vehiclefitment_vehiclesubmodel.id = django_vehiclefitment_vehicle.sub_model_id" if sub_model and not isinstance(sub_model, int) else ""
        sub_model_condition_sql = f"AND django_vehiclefitment_vehiclesubmodel.name = '{sub_model}'" if not isinstance(sub_model, int) else f"AND django_vehiclefitment_vehicle.sub_model_id = {sub_model}"

    if engines:
        if isinstance(engines[0], int):
            engine_condition_sql = f"AND django_vehiclefitment_vehicle.engine_id IN ({','.join(map(lambda x: str(x), engines))})"
        else:
            engine_configurations = map(lambda x: "'" + x + "'", engines)
            engine_condition_join = "INNER JOIN django_vehiclefitment_vehicleengine ON django_vehiclefitment_vehicle.engine_id = django_vehiclefitment_vehicleengine.id"
            engine_condition_sql = f"AND django_vehiclefitment_vehicleengine.configuration IN ({','.join(engine_configurations)})"

    years_conditions = list()

    if end_year == "up":
        end_year = datetime.datetime.utcnow().year
    for year in range(start_year, end_year + 1):
        years_conditions.append(f"({year} BETWEEN {product_fitment_table_name}.start_year and {product_fitment_table_name}.end_year)")
    years_condition_sql = " OR ".join(years_conditions)
    queryset = queryset.extra(where=[f"""
        EXISTS (
            SELECT 1 FROM {product_fitment_table_name} 
            INNER JOIN django_vehiclefitment_vehicle ON django_vehiclefitment_vehicle.id = {product_fitment_table_name}.vehicle_id
            {make_condition_join}
            {model_condition_join}
            {sub_model_condition_join}
            {engine_condition_join}
            WHERE {product_fitment_table_name}.product_id = {product_table_name}.id
            {make_condition_sql}
            {model_condition_sql}
            {sub_model_condition_sql}
            {engine_condition_sql}
            AND ({years_condition_sql})
        )
    """])
    return queryset
