# Load table
# MUST RUN THE excel_to_csv.sh FIRST
my_table <- read.csv("identifier_table.csv")

# Extract metadata
meta_tab <- my_table[c(1:28), c(10:50)]

# Extract Data
data_tab <- my_table[-c(1:28), -c(10:50)]

# Format missing values in third column (check if yours is missing too or not)
data_tab[-1,2] <- data_tab[-1,3]
data_tab <- data_tab[,-3]

# Format column names
colnames(data_tab) <- data_tab[1,]
data_tab <- data_tab[-1,]

# Remove empty row
data_tab <- data_tab[which(!is.na(data_tab$`Prevalence in Paraf. Controls`)),]
