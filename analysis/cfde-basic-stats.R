# cfde program basic stats
library(ggplot2)
library(dplyr)
library(jsonlite)
library(ggrepel)
library(cowplot)
library(scales)
library(lubridate)

theme_set(theme_bw())

black <- "#000000"
blue <- "#2AC9E6"
grey <- "#808080"

fill_manual <- c("CFDE Website" = black, "Cites Flagship" = blue, "Keyword Search" = grey)

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
      source == "cfde_website" ~ "CFDE Website",
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
filter(full_dataset, type == cfde) %>%
  group_by(program) %>%
  distinct(pmid, .keep_all = T) %>%
  ggplot(aes(x = forcats::fct_infreq(program), fill = source)) +
  geom_bar(alpha = 0.8) +
  labs(x = "", y = "Total Citations") +
  scale_fill_manual(values = fill_manual) +
  theme_axis_legend +
  theme(
    axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1),
    legend.position = c(0.9, 0.9)
  )

ggsave("cfde_dcc_citations.png", width = 10, height = 7)


cfde <- "cfde_dcc"
rcr <- filter(full_dataset, type == cfde) %>%
  group_by(program) %>%
  distinct(pmid, .keep_all = T) %>%
  summarize(n = n(), mean_rcr = mean(icite_rcr, na.rm = T))

marg <- 10
ggplot(rcr, aes(x = program, y = mean_rcr, fill = program)) +
  geom_bar(alpha = 0.8, stat = "identity") +
  labs(x = "", y = "Mean RCR") +
  theme_axis_legend +
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1)) +
  scale_fill_brewer(palette = "Paired") +
  theme(
    legend.position = "none",
    plot.margin = margin(marg, marg, marg, marg)
  )
ggsave("cfde_dcc_rcr.png", width = 11, height = 8)

ggplot(rcr, aes(x = mean_rcr, y = n, color = program)) +
  geom_point(size = 6) +
  theme_axis_legend +
  theme(legend.position = "none") +
  scale_color_brewer(palette = "Paired") +
  labs(x = "Mean RCR", y = "Number of Citations") +
  geom_label_repel(
    label = rcr$program,
    force = 2,
    show.legend = F,
    box.padding = 0.4,
    fontface = "bold",
    color = black
  )

ggsave("cfde_rcr_scatter.png", width = 8, height = 6)


rcr_source <- filter(full_dataset, type == cfde) %>%
  group_by(program, source) %>%
  distinct(pmid, .keep_all = T) %>%
  summarize(n = n(), mean_rcr = mean(icite_rcr, na.rm = T))

ggplot(rcr_source, aes(x=program,y=mean_rcr, fill=source)) +
  geom_bar(alpha=0.8, stat="identity", position=position_dodge2(preserve="single")) +
  scale_fill_manual(values = fill_manual) +
  theme_axis_legend +
  theme(
    axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1),
    legend.position = c(0.9, 0.9)
  ) +
  labs(x="", y = "Mean RCR")

ggsave("cfde_dcc_by_category_rcr.png", width = 10, height = 7)

full_dataset %>%
  mutate(year = lubridate::year(lubridate::as_date(oa_publication_date)))

individual_dcc_rcr_source <- function(data, program_target, legend_pos = c(0.2, 0.9)) {
  filtered_data <- filter(data, program == program_target, oa_publication_year > 1999) %>%
    #mutate(oa_publication_date = lubridate::as_date(oa_publication_date)) %>%
    distinct(pmid, .keep_all = T)

  # Citations plot
  histogram <-ggplot(filtered_data, aes(x = oa_publication_year, fill = source)) +
    geom_bar(alpha = 0.8) +
    labs(x = "", y = paste(program_target, "Citations", sep = " ")) +
    scale_fill_manual(values = fill_manual, drop = T) +
    theme_axis_legend +
    theme(
      axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1),
      legend.position = legend_pos
    )
  # RCR Plot
  filtered_rcr <- filtered_data %>%
    group_by(oa_publication_year, source) %>%
    summarize(mean_rcr = mean(icite_rcr, na.rm = T), n = n()) %>%
    filter(n >= 2) %>%
    tidyr::drop_na()

  rcr_plot <- ggplot(filtered_rcr, aes(x = source, y = mean_rcr, fill = source)) +
    geom_bar(alpha = 0.8, stat = "identity") +
    labs(x = "", y = "Mean RCR") +
    scale_fill_manual(values = fill_manual, drop = T) +
    theme_axis_legend +
    theme(
      axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1),
      legend.position = "none"
    )
  plot_grid(histogram, rcr_plot, labels = c("A.", "B."), vjust = c(1, 1), label_size = 12)
}

similar_dcc_plot <- function(data, program_target, legend_pos = c(0.2, 0.9)){
  filtered_dataset <- data %>%
    filter(competes_with == program_target | program == program_target, oa_publication_year > 1999) #%>%
    #mutate(oa_publication_year = lubridate::year(oa_publication_date)))
  histogram <- ggplot(filtered_dataset, aes(x = oa_publication_year, fill = program)) +
    geom_bar(alpha = 0.8, position=position_dodge2(preserve="single")) +
    labs(x = "", y = "Total Citations") +
    scale_fill_brewer(palette = "Paired") +
    theme_axis_legend +
    theme(
    axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1),
    legend.position = legend_pos
    )

  filtered_rcr <- filtered_dataset %>%
    group_by(program) %>%
    summarize(mean_rcr = mean(icite_rcr, na.rm = T), n = n()) %>%
    filter(n >= 2) %>%
    tidyr::drop_na()

  rcr_comp <- ggplot(filtered_rcr, aes(x = program, y = mean_rcr, fill = program)) +
    geom_bar(alpha = 0.8, stat = "identity") +
    labs(x = "", y = "Mean RCR") +
    scale_fill_brewer(palette = "Paired") +
    theme_axis_legend +
    theme(
    axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1),
    legend.position = "none"
    )
  plot_grid(histogram, rcr_comp, labels = c("A.", "B."), vjust = c(1, 1), label_size = 12)
  }


#### Plots for similar and non-similar DCCs ####

individual_dcc_rcr_source(full_dataset, "Metabolomics Workbench",  c(0.25, 0.85))
ggsave("metabwork_dcc_plots.png", width=8, height=5)

similar_dcc_plot(full_dataset, "Metabolomics Workbench", c(0.32,0.9))
ggsave("metabwork_and_simialr_dcc_plots.png", width=9, height=5)

individual_dcc_rcr_source(full_dataset, "GlyGen", c(0.3, 0.88))
ggsave("glygen_dcc_plots.png", width=8,height=4)

similar_dcc_plot(full_dataset, "GlyGen", c(0.3, 0.88))
ggsave("glygen_and_similar_dcc_plots.png", width=8,height=4)

individual_dcc_rcr_source(full_dataset, "GTEx", c(0.25, 0.85))
ggsave("gtex_dcc_plots.png", width=8, height=4)

similar_dcc_plot(full_dataset, "GTEx", c(0.3, 0.88))
ggsave("gtex_and_similar_dcc_plots.png", width=9,height=5)

individual_dcc_rcr_source(full_dataset, "IDG", c(0.3, 0.88))
ggsave("idg_dcc_plots.png", width=8, height=4)

similar_dcc_plot(full_dataset, "IDG", c(0.3,0.88))
ggsave("idg_and_similar_dcc_plots.png", width=8, height=4)

individual_dcc_rcr_source(full_dataset, "MoTrPAC", c(0.3, 0.88))
ggsave("motrpac_dcc_plots.png", width=8, height=4)

similar_dcc_plot(filter(full_dataset, program != "Exercise Transcriptome Meta-analysis"), "MoTrPAC", c(0.2,0.9))
ggsave("motrpac_and_similar_dcc_plots.png", width=8, height=4)

individual_dcc_rcr_source(full_dataset, "ExRNA", c(0.3, 0.88))
ggsave("exrna_dcc_plots.png", width=8, height=4)

similar_dcc_plot(full_dataset, "ExRNA", c(0.2,0.88))
ggsave("exrna_and_similar_dcc_plots.png", width=8, height=4)

# see bottom of script for kids first
#individual_dcc_rcr_source(full_dataset, "Kids First", c(0.3, 0.88))
#ggsave("kidsfirst_dcc_plots.png", width=8, height=4)

similar_dcc_plot(full_dataset, "Kids First", c(0.2,0.88))
ggsave("kidsfirst_and_similar_dcc_plots.png", width=8, height=4)

#### Plots for Non-comparable DCCs ####
individual_dcc_rcr_source(full_dataset, "LINCS", c(0.3, 0.85))
ggsave("lincs_dcc_plots2.png", width = 8, height = 4)


individual_dcc_rcr_source(full_dataset, "HuBMAP", c(0.3, 0.85))
ggsave("hubmap_dcc_plots2.png", width = 9, height = 4)

individual_dcc_rcr_source(full_dataset, "SPARC", c(0.3, 0.85))
ggsave("sparc_dcc_plots2.png", width = 9, height = 4)

individual_dcc_rcr_source(full_dataset, "HMP", c(0.3, 0.85))
ggsave("hmp_dcc_plots2.png", width = 9, height = 4)

individual_dcc_rcr_source(full_dataset, "4D Nucleome", c(0.3, 0.85))
ggsave("4dn_dcc_plots2.png", width = 9, height = 5)


### DCC Summaries Without Comparable External Repositories ####

#
# individual_dcc <- function(data, program_target, legend_pos = c(0.2, 0.9)) {
#
#   filtered_data <- filter(data, program == program_target) %>%
#     distinct(pmid, .keep_all = T)
#
#   filtered_range <- filtered_data$oa_publication_year
#     x_continuous <- scale_x_continuous(
#     breaks = seq(min(filtered_range), max(filtered_range), by = 5),
#     labels = seq(min(filtered_range), max(filtered_range), by = 5),
#     limits= c(min(filtered_range), max(filtered_range))
#   )
#
#   # Citations plot
#   histogram <- ggplot(filtered_data, aes(x = oa_publication_year, fill = source)) +
#     geom_bar(alpha = 0.8) +
#     labs(x = "", y = paste(program_target, "Citations", sep = " ")) +
#     scale_fill_manual(values = fill_manual) +
#     theme_axis_legend +
#     x_continuous +
#     theme(
#       axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1),
#       legend.position = legend_pos
#     )
#   # RCR Plot
#   filtered_rcr <- filtered_data %>%
#     group_by(oa_publication_year, source) %>%
#     summarize(mean_rcr = mean(icite_rcr, na.rm = T), n = n()) %>%
#     filter(n >= 2) %>%
#     tidyr::drop_na()
#
#   rcr_plot <- ggplot(filtered_rcr, aes(x = oa_publication_year, y = mean_rcr, fill = source)) +
#     geom_bar(alpha = 0.8, stat = "identity") +
#     labs(x = "", y = paste(program_target, "mean RCR", sep = " ")) +
#     scale_fill_manual(values = fill_manual) +
#     x_continuous +
#     theme_axis_legend +
#     theme(
#       axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1),
#       legend.position = "none"
#     )
#   filtered_data %>%
#     summarize(mean_rcr = mean(icite_rcr, na.rm=T)) %>%
#     print()
#   plot_grid(histogram, rcr_plot)
# }

program_tar = "Kids First"

filtered_data <- filter(full_dataset, program == program_tar)

histogram <- ggplot(filtered_data, aes(x = oa_publication_year, fill = source)) +
  geom_bar(alpha = 0.8) +
  labs(x = "", y = paste(program, "Citations", sep = " ")) +
  scale_fill_manual(values = fill_manual, drop = T) +
  theme_axis_legend +
  theme(
    axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1),
    legend.position = c(0.3,0.88)
  )
  # RCR Plot

filtered_rcr <- filtered_data %>%
    group_by(oa_publication_year, source) %>%
    summarize(mean_rcr = mean(icite_rcr, na.rm = T), n = n()) %>%
    filter(n >= 2) %>%
    tidyr::drop_na()

rcr_plot <- ggplot(filtered_rcr, aes(x = source, y = mean_rcr, fill = source)) +
    geom_bar(alpha = 0.8, stat = "identity") +
    labs(x = "", y = "Mean RCR") +
    scale_fill_manual(values = fill_manual, drop = T) +
    theme_axis_legend +
    theme(
      axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1),
      legend.position = "none"
    )

plot_grid(histogram, rcr_plot, labels = c("A.", "B."), vjust = c(1, 1), label_size = 12)

ggsave("kidsfirst_dcc_plot.png", width=8, height=4)
