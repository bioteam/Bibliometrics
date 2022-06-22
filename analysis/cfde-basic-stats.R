# cfde program basic stats
library(ggplot2)
library(dplyr)
library(jsonlite)

theme_set(theme_bw())

black <- "#000000"
blue <- "#2AC9E6"
grey <- "#808080"

theme_axis_legend <- theme(
  text = element_text(size = 14, face = "bold"),
  plot.caption = element_text(size = 10, hjust = 0, face = "plain"),
  legend.title = element_blank(),
  legend.background = element_blank(),
  axis.text = element_text(size = 18, face = "bold", color = black),
  axis.line = element_line(color = black, size = 0.6)
)

full_dataset <- bind_rows(purrr::map(list.files(path="../data/final", pattern="_icite_oa_results.json", full.names = T), fromJSON)) %>%
  mutate(source = case_when(source == "cfde_website" ~ "CFDE Website",
                            source == "cites_a_flagship" ~ "Cites Flagship",
                            source == "keyword_search" ~ "Keyword Search",
                            TRUE ~ "unknown"),
         program = if_else(program == "4DN", "4D Nucleome", program)) %>%
  tidyr::drop_na(pmid)



cfde <- "cfde_dcc"
filter(full_dataset, type == cfde) %>%
  group_by(program) %>%
  distinct(pmid, .keep_all = T) %>%
  ggplot(aes(x=forcats::fct_infreq(program), fill=source)) +
  geom_bar(alpha=0.8) +
  labs(x="", y="Total Citations") +
  scale_fill_manual(values = c(black, blue, grey)) +
  theme_axis_legend +
  theme(axis.text.x = element_text(angle=45, vjust=1, hjust=1),
        legend.position=c(0.9,0.9))

ggsave("cfde_dcc_citations.png", width=10,height=7)


cfde <- "cfde_dcc"
rcr <- filter(full_dataset, type == cfde, source == "CFDE Website" | source == "Cites Flagship") %>%
  group_by(program) %>%
  distinct(pmid, .keep_all = T) %>%
  summarize(n=n(), mean_rcr = mean(icite_rcr, na.rm=T))

ggplot(rcr, aes(x=program, y=mean_rcr, fill=program))+
  geom_bar(alpha=0.8, stat="identity") +
  labs(x="", y="Mean RCR") +
#  scale_fill_manual(values = c(black, blue, grey)) +
  theme_axis_legend +
  theme(axis.text.x = element_text(angle=45, vjust=1, hjust=1)) +
  scale_fill_brewer(palette = "Paired") +
  theme(legend.position="none")
ggsave("cfde_dcc_rcr.png", width=10, height=7)
# what is a fair guide? provide clear methods, what do we suggest as a fair approach for comparing repos with older data
# difficult on affiliation, and compare the density map
# HMP is mostly coming from dbGAP, another way of thinking about it
# mesh terms over time, is it manual,
