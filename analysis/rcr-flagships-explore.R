# rcr for flagships
library(ggplot2)
library(dplyr)
library(jsonlite)

theme_set(theme_bw())

black <- "#000000"
blue <- "#2AC9E6"
grey <- "#808080"
red <- "#CC0000"
green <- "#008F00"

CHECK <- "*"
PARTIAL <- "~"
ABSENT <- "x"

fill_manual <- c("Common Fund Website" = black, "Cites Flagship" = blue, "Keyword Search" = grey)

theme_axis_legend <- theme(
  text = element_text(size = 14, face = "bold"),
  plot.caption = element_text(size = 10, hjust = 0, face = "plain"),
  legend.title = element_blank(),
  legend.background = element_blank(),
  axis.text = element_text(size = 18, face = "bold", color = black),
  axis.line = element_line(color = black, size = 0.6)
)

full_dataset <- bind_rows(purrr::map(list.files(path = "../data/final", pattern = "_icite_oa_results.json", full.names = T), fromJSON)) %>%
  mutate(
    source = case_when(
      source == "cfde_website" ~ "Common Fund Website",
      source == "cites_a_flagship" ~ "Cites Flagship",
      source == "keyword_search" ~ "Keyword Search",
      TRUE ~ "unknown"
    ),
    program = if_else(program == "4DN", "4D Nucleome", program),
    program = if_else(program == "Glycoscience", "GlyGen", program),
    source = if_else(source == "unknown" & program == "Metabolomics Workbench", "Cites Flagship", source)
  ) %>%
  filter(oa_publication_year > 1999) %>%
  tidyr::drop_na(pmid, oa_publication_year)


cfde <- "cfde_dcc"
rcr_excl <- filter(full_dataset, type == cfde, source != "Common Fund Website") %>%
  group_by(program) %>%
  distinct(pmid, .keep_all = T) %>%
  summarize(n = n(), mean_rcr = mean(icite_rcr, na.rm = T),
            median_rcr = median(icite_rcr, na.rm=T),
            sd_rcr = sd(icite_rcr, na.rm=T),
            sem_rcr = sd_rcr/n,
            coeff_var = sd_rcr/mean_rcr)

progs <- unique(full_dataset$program)
label_dataset <- data.frame(program = as.factor(progs)) %>%
  mutate(flag_sym = case_when(program == "4D Nucleome" ~ CHECK,
                              program == "GlyGen" ~ CHECK,
                              program == "MoTrPAC" ~ CHECK,
                              program == "Kids First" ~ ABSENT,
                              program == "GTEx" ~ PARTIAL,
                              program == "HuBMAP" ~ PARTIAL,
                              program == "SPARC" ~ ABSENT,
                              program == "IDG" ~ PARTIAL,
                              program == "LINCS" ~ PARTIAL,
                              program == "Metabolomics Workbench" ~ PARTIAL,
                              program == "HMP" ~ ABSENT,
                              program == "ExRNA" ~ PARTIAL,
                              TRUE ~ "???")) %>%
  left_join(., rcr_excl, by="program") %>%
    mutate(y_pos_n = if_else(flag_sym == ABSENT, n+200, n+100),
         y_pos_rcr = if_else(flag_sym == ABSENT, mean_rcr+1, mean_rcr+0.5),
         y_pos_med_rcr = if_else(flag_sym == ABSENT, median_rcr+0.25, median_rcr+0.25))

marg <- 10
ggplot(rcr_excl, aes(x = program, y = mean_rcr, fill = program)) +
  geom_bar(alpha = 0.8, stat = "identity") +
  labs(x = "", y = "Mean RCR") +
  #geom_errorbar(aes(ymin=mean_rcr - sem_rcr, ymax=mean_rcr + sem_rcr), width=.2) +
  theme_axis_legend +
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1)) +
  scale_fill_brewer(palette = "Paired") +
  geom_text(aes(x=program, y=y_pos_rcr),
            label=filter(label_dataset, flag_sym!="???")$flag_sym,
            data=filter(label_dataset, flag_sym!="???"), inherit.aes=F,
            size=8,
            fontface="bold") +
  theme(
    legend.position = "none",
    plot.margin = margin(marg, marg, marg, marg)
  )

ggsave("cfde_dcc_rcr_excl_cf.png", width = 11, height = 8)

