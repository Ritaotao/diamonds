# list.of.packages <- c("httr", "jsonlite")
#new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
# if(length(new.packages)) install.packages(new.packages)

library(httr)
library(jsonlite)
HOME_URL <- 'http://www.bluenile.com'
API_URL <- 'http://www.bluenile.com/api/public/diamond-search-grid/v2'

landing_page <- GET(HOME_URL)
cookie <- cookies(landing_page)
print(cookie)

params <- list(
    startIndex = 0,
    pageSize = 1000,
    country = "USA",
    language = "en-US",
    currency = "USD",
    sortColumn = "price",
    sortDirection = "asc",
    shape="RD"
)

raw.result <- GET(API_URL, query = params)
print(raw.result$status_code)

print(content(raw.result, "text", encoding = "ISO-8859-1"))