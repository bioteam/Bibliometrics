# cfde program basic stats
library(ggplot2)
library(dplyr)
library(jsonlite)

theme_set(theme_bw())
black <- "#000000"
blue <- "#2AC9E6"
theme_axis_legend <- theme(
  text = element_text(size = 14, face = "bold"),
  plot.caption = element_text(size = 10, hjust = 0, face = "plain"),
  legend.title = element_blank(),
  legend.background = element_blank(),
  axis.text = element_text(size = 18, face = "bold", color = black),
  axis.line = element_line(color = black, size = 0.6)
)

data <- bind_rows(purrr::map(c("cfde_website_data.json", "from_flagship.json"), fromJSON)) %>%
  mutate(program = if_else(program == "4D nucleome", "4D Nucleome", program)) %>%
  filter(publication_year < 2022) %>%
  mutate(source = case_when(source == "cfde_website" ~ "CFDE Funding",
                            source == "cites_a_flagship" ~ "Cites a Flagship",
                            TRUE ~ source))

filter(data, program == "Metabolomics") %>%
  distinct(pmid, .keep_all = T) %>%
  ggplot(aes(x=publication_year, fill=source)) +
  geom_bar(alpha=0.8) +
  labs(x="Year", y="Number of Citations", title="Metabolomics Citations") +
  scale_fill_manual(values = c(black, blue)) +
  theme_axis_legend
ggsave("metabolomics_citations.png")


# what is a fair guide? provide clear methods, what do we suggest as a fair approach for comparing repos with older data
# difficult on affiliation, and compare the density map
# HMP is mostly coming from dbGAP, another way of thinking about it
# mesh terms over time, is it manual,
