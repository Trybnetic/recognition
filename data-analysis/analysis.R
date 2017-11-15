#!/usr/bin/Rscript

if (!("mpt" %in% installed.packages())) {
  stop("Please install package mpt first")
}

cities <- read.table("../raw-data/cities.txt", header=TRUE, sep=";", as.is=TRUE)

check_correct_answers <- function(line){
  cityA <- line[1]
  cityB <- line[2]
  response <- line[3]
  ranking="english"
  if(ranking == "german") {
    rank_cityA <- cities[cities$name == cityA,]$rank_de
    rank_cityB <- cities[cities$name == cityB,]$rank_de
  }
  if(ranking == "english") {
    rank_cityA <- cities[cities$name == cityA,]$rank_en
    rank_cityB <- cities[cities$name == cityB,]$rank_en
  }

  if(rank_cityA < rank_cityB) {
    if(response == cityA) {
      return("y")
    } else {
      return("n")
    }
  } else {
    if(response == cityA) {
      return("n")
    } else {
      return("y")
    }
  }
}


################################################################################
###                           Begin Skript                                   ###
################################################################################

control_ids <- c(1:9, 19:27)
experimental_ids <- c(10:18,28:36)

files <- data.frame(name=unlist(strsplit(list.files(path="../raw-data/recognition/",
                                         pattern="subj.*\\-pc.txt"), split="-pc.txt")),
                    stringsAsFactors=F)

files$path <- apply(files, 1, function(x) { paste("../raw-data/", x, sep="")})

files$group = as.numeric(unlist(strsplit(unlist(strsplit(files$path, split="-"))[3 * (1:length(files$path)) - 1], split="subj"))[2* (1:length(files$path))]) %in% experimental_ids

experimental_group <- files$name[files$group]
controll_group <- files$name[!files$group]

calculate_categories <- function(participant){

  dat <- read.table(paste("../raw-data/recognition/", participant, "-pc.txt", sep=""), skip=1, header=T, sep=";")

  # Loading knowledge of participant
  knowledge <- read.table(paste("../raw-data/knowledge/", participant,"-know.txt", sep=""), skip=1, header=T, sep=";")[c(1,2)]

  knows_city <- function(city){
      if(knowledge[knowledge$Name == city,][2]=="y"){
        return("y")
      } else {
        return("n")
      }
  }

  dat$is_correct <- apply(dat,1,check_correct_answers)
  dat$knows_cityA <- apply(dat[1],1,knows_city)
  dat$knows_cityB <- apply(dat[2],1,knows_city)


  categorize <- function(line){
    response <- line[3]
    is_correct <- line[5] == "y"
    knows_cityA <- line[6] == "y"
    knows_cityB <- line[7] == "y"
    # Both objects recognized
    if(knows_cityA & knows_cityB){
      # Valid knowledge
      if(is_correct){
        return(1)
      # invalid knowledge
      } else {
        return(2)
      }
    }

    # Neither object recognized
    if(!knows_cityA & !knows_cityB){
      # Valid guess
      if(is_correct){
        return(3)
      # invalid guess
      } else {
        return(4)
      }
    }

    # One object recognized
    if(knows_cityA | knows_cityB){
      # Choice of recognized object
      if(knows_city(response) == "y") {
        # correct
        if(is_correct){
          return(5)
        # false
        } else {
          return(6)
        }
      # Choice of unrecognized object
      } else {
        if(is_correct){
          return(8)
        # false
        } else {
          return(7)
        }
      }
    }
  }


  dat$category <- apply(dat,1,categorize)

  result <- table(dat$category)

  return(dat$category)
}

################################################################################
###                               ERGEBNIS                                   ###
################################################################################

res_exp <- table(Reduce(c,tapply(X=experimental_group, FUN=calculate_categories, INDEX=experimental_group)))

res_con <- table(Reduce(c,tapply(X=controll_group, FUN=calculate_categories, INDEX=controll_group)))

Freq_exp <- as.data.frame(res_exp)$Freq
Freq_con <- as.data.frame(res_con)$Freq

require(mpt)

spec <- mptspec('rmodel')

mpt.exp <- mpt(spec, Freq_exp)
mpt.con <- mpt(spec, Freq_con)

spec2 <- mptspec('rmodel', .replicates=2, .restr=list(r1=r, r2=r))
mpt.test <- mpt(spec2, c(Freq_exp, Freq_con))


spec3 <- mptspec('rmodel', .replicates=2)
mpt.test2 <- mpt(spec3, c(Freq_exp, Freq_con))

spec4 <- mptspec('rmodel', .replicates=2, .restr=list(g1=g, g2=g))
mpt.test3 <- mpt(spec4, c(Freq_exp, Freq_con))

spec5 <- mptspec('rmodel', .replicates=2, .restr=list(g1=g, g2=g, r1=r, r2=r))
mpt.test4 <- mpt(spec4, c(Freq_exp, Freq_con))


plot_parameter_differnces <- function(par){
  par.exp <- coef(mpt.exp, logit=F)[par]
  par.con <- coef(mpt.con, logit=F)[par]

  par.confint.exp <- confint(mpt.exp, logit=F)[par,]
  par.confint.con <- confint(mpt.con, logit=F)[par,]

  barplot(c(par.exp,par.con),
#          main=paste("Effect of Recognition Heuristic on parameter",par, sep=" "),
          main=paste("Parameter",par, sep=" "),
          ylim=c(0,1),
          ylab="Parameter estimate (95% CI)",
          xlab="Experimental Condition",
          names.arg=c("RH","Control"))
  arrows(c(0.7,1.9), c(par.confint.exp["2.5 %"], par.confint.con["2.5 %"]),
         c(0.7,1.9), c(par.confint.exp["97.5 %"], par.confint.con["97.5 %"]),
        .2, 90, 3)
  box()
}

pool_correct <- function(freq) {
  return(c(freq[1],
           freq[2],
           freq[3],
           freq[4],
           freq[5] + freq[8],
           freq[6] + freq[7]))
}

pool_knowledge <- function(freq) {
  return(c("both cities" = freq[1]+ freq[2],
           "neither city" = freq[3] + freq[4],
           "one city" = freq[5] + freq[8] + freq[6] + freq[7]))
}

plot_knowledge <- function(par, freqA, freqB){
  catA <- freqA[par]
  catB <- freqB[par]

  barplot(c(catA,catB),
          main=par,
          ylim=c(0,1500),
          ylab="Frequency",
          xlab="Experimental Condition",
          names.arg=c("RH","Control"))
  box()
}

par(mfrow=c(2,2))
tapply(X=c("b","g","r","a"), FUN=plot_parameter_differnces, INDEX=c("b","g","r","a"))


par(mfrow=c(2,2))
tapply(X=c("both cities", "neither city", "one city"),
       FUN=function(x){plot_knowledge(x,pool_knowledge(Freq_exp), pool_knowledge(Freq_con))},
       INDEX=c("both cities", "neither city", "one city"))


know_freq_long <- data.frame(knowledge = c(rep(c("both cities", "neither city", "one city"),
                                          times = pool_knowledge(Freq_exp)),
                                      rep(c("both cities", "neither city", "one city"),
                                          times = pool_knowledge(Freq_con))),
                             condition = c(rep(c("RH"),
                                            times = sum(pool_knowledge(Freq_exp))),
                                           rep(c("control"),
                                            times = sum(pool_knowledge(Freq_con)))))

correct.exp <- pool_correct(Freq_exp)
correct.con <- pool_correct(Freq_con)
correct_freq_long <- data.frame(knowledge = c(rep(c("both cities (correct)", "both cities (false)" ,
                                                    "neither city (correct)", "neither city (false)",
                                                    "one city (correct)", "one city (false)"),
                                              times = correct.exp),
                                              rep(c("both cities (correct)", "both cities (false)" ,
                                                    "neither city (correct)", "neither city (false)",
                                                    "one city (correct)", "one city (false)"),
                                              times = correct.con)),
                                condition = c(rep(c("RH"),
                                            times = sum(correct.exp)),
                                           rep(c("control"),
                                            times = sum(correct.con))))


par(mfrow=c(2,1))
mosaicplot(table(know_freq_long), main="Knowledge as a function of experimental condition", shade=T)
chisq.test(table(know_freq_long))

mosaicplot(table(correct_freq_long), main="Correctness as a function of experimental condition", shade=T)
chisq.test(table(correct_freq_long))

par(mfrow=c(1,1))

exp.all <- sum(correct.exp)
exp.T <- sum(correct.exp[c(1,3,5)])/exp.all
exp.F <- sum(correct.exp[c(2,4,6)])/exp.all

con.all <- sum(correct.con)
con.T <- sum(correct.con[c(1,3,5)])/exp.all
con.F <- sum(correct.con[c(2,4,6)])/exp.all


confint.correct <- function(p,n){
  l <- p - 1.96 * sqrt(p * (1 -p)/n)
  r <- p + 1.96 * sqrt(p * (1 -p)/n)
  return(c(l,r))
}

exp.confint <- confint.correct(exp.T,exp.all)
con.confint <- confint.correct(con.T,con.all)

barplot(c(exp.T,con.T),
        main="Correctness",
        ylim=c(0,1),
        ylab="correctness",
        xlab="Experimental Condition",
        names.arg=c("RH","Control"))
#arrows(c(0.7,1.9), c(exp.confint[1], con.confint[1]),
#       c(0.7,1.9), c(exp.confint[2], con.confint[2]),
#      .2, 90, 3)
box()
