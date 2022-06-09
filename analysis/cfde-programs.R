# CFDE programs analysis
library(dplyr)
library(ggplot2)
library(jsonlite)
theme_set(theme_bw())

data <- bind_rows(purrr::map(list.files(path="data", pattern="-GEO.json",full.names = T), fromJSON))

data %>%
  filter(program == c("Metabolomics",
                      "4D Nucleome",
                      "Gabriella Miller Kids First",
                      "Genotype-Tissue Expression (GTEx)")) %>%
  filter(publication_year > 2005) %>%
  ggplot(aes(x=publication_year, fill=program)) +
  geom_bar(position=position_dodge2(preserve="single"),
           size=0.4,alpha=0.8) +
  labs(x="Year", y="Publications Citing")




