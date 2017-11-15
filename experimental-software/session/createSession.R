# createSession.R
# Session files for paired-comparison experiment (Hilbig et al., 2010, Exp. 6)
#
# Input:  Cities.txt
# Output: ses??-g.txt, ?? in 01, ..., nsubj; g in 0, 1
#
# Initial version: Jun/09/2016, DF
# Last mod:        Jun/15/2016, FW


library(eba)
set.seed(1027)

nsubj  <- 36
nstim  <- 17
ngrp   <-  2  # instruction (0, 1)
npairs <- nstim*(nstim - 1)/2

bp <- balanced.pcdesign(nstim)

## 2 (instruction type) by 2 (within-pair order, list) between subjects design
dat <- data.frame(subjid = rep(1:nsubj, each=npairs),
                  pairid = rep(1:npairs, nsubj),
                    list = rep(c("A", "B"), each=npairs*nsubj/2),
                   instr = rep(rep(0:1, each=npairs*nsubj/2/ngrp), ngrp),
                    pair = c(replicate(nsubj/2, sample(bp$listA)),
                             replicate(nsubj/2, sample(bp$listB))))

cities <- read.table("cities.txt", header=TRUE, sep=";", as.is=TRUE)
dat$stim1 <- cities[substr(dat$pair, 1, 1), "name"]
dat$stim2 <- cities[substr(dat$pair, 2, 2), "name"]

for (i in unique(dat$subjid)) {
  fname <- paste0("ses", sprintf("%02d", i), "-",
                  unique(dat$instr[dat$subjid == i]), ".txt")
  fout <- file(fname, "a")  # open in append mode
  
  writeLines(
    with(dat[dat$subjid == i, ],
         paste0("trial('", stim1[1:(npairs/4)], "', '",
                           stim2[1:(npairs/4)], "')")), fout
  )
  writeLines("pause('Block 1 von 4 geschafft')", fout)
  writeLines(
    with(dat[dat$subjid == i, ],
         paste0("trial('", stim1[(npairs/4 + 1):(npairs/2)], "', '",
                           stim2[(npairs/4 + 1):(npairs/2)], "')")), fout
  )
  writeLines("pause('Block 2 von 4 geschafft')", fout)
  writeLines(
    with(dat[dat$subjid == i, ],
         paste0("trial('", stim1[(npairs/2 + 1):(3*npairs/4)], "', '",
                           stim2[(npairs/2 + 1):(3*npairs/4)], "')")), fout
  )
  writeLines("pause('Block 3 von 4 geschafft')", fout)
  writeLines(
    with(dat[dat$subjid == i, ],
         paste0("trial('", stim1[(3*npairs/4 + 1):npairs], "', '",
                           stim2[(3*npairs/4 + 1):npairs], "')")), fout
  )
     
  close(fout)
}

# Check
# for (fn in dir(pattern="ses..-[01].txt")) {
#   s <- readLines(fn)
#   print(
#     apply(do.call(rbind, strsplit(gsub("trial\\((.+), (.+)\\)",
#                                        "\\1;\\2", s), ";")), 2, table)
#   )
# }

