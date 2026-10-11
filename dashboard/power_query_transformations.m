/* ==============================================================================
   power_query_transformations.m
   Power Query (M) ETL Scripts for Power BI Ingestion
============================================================================== */

// ------------------------------------------------------------------------------
// Query 1: dim_customer
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(#"DataFolderPath" & "dim_customer.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"customer_id", type text},
        {"customer_name", type text},
        {"customer_segment", type text},
        {"gender", type text},
        {"age", Int64.Type}
    }),
    #"Cleaned Strings" = Table.TransformColumns(#"Changed Type",{
        {"customer_name", Text.Trim, type text},
        {"customer_segment", Text.Trim, type text}
    })
in
    #"Cleaned Strings"

// ------------------------------------------------------------------------------
// Query 2: dim_product
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(#"DataFolderPath" & "dim_product.csv"), [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"product_id", type text},
        {"product_name", type text},
        {"category", type text},
        {"sub_category", type text},
        {"brand", type text},
        {"standard_retail_price", type number}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// Query 3: dim_location
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(#"DataFolderPath" & "dim_location.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"location_id", type text},
        {"city", type text},
        {"state", type text},
        {"country", type text},
        {"region", type text}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// Query 4: dim_date
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(#"DataFolderPath" & "dim_date.csv"), [Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"date_key", type text},
        {"full_date", type date},
        {"year", Int64.Type},
        {"quarter", Int64.Type},
        {"quarter_name", type text},
        {"month", Int64.Type},
        {"month_name", type text},
        {"week_of_year", Int64.Type},
        {"day_of_month", Int64.Type},
        {"day_name", type text},
        {"is_weekend", Int64.Type}
    })
in
    #"Changed Type"

// ------------------------------------------------------------------------------
// Query 5: fact_sales
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(#"DataFolderPath" & "fact_sales.csv"), [Delimiter=",", Columns=23, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"order_id", type text},
        {"order_item_id", type text},
        {"order_date", type text},
        {"ship_date", type text},
        {"customer_id", type text},
        {"product_id", type text},
        {"location_id", type text},
        {"ship_mode", type text},
        {"payment_method", type text},
        {"quantity", Int64.Type},
        {"unit_price", type number},
        {"discount_rate", type number},
        {"gross_sales", type number},
        {"net_sales", type number},
        {"cost_amount", type number},
        {"profit", type number},
        {"profit_margin_pct", type number},
        {"shipping_cost", type number},
        {"shipping_duration_days", Int64.Type},
        {"discount_bracket", type text},
        {"return_flag", Int64.Type},
        {"rating", Int64.Type},
        {"is_profitable", Int64.Type}
    })
in
    #"Changed Type"
