library(plyr)
library(doMC)
library(ggplot2)
library(data.table)
registerDoMC(cores=detectCores())

MEASURES        <- ["error", "pressure"]
PATH_NAMES      <- ["path1", "path2", "path3"]
FEEDBACK_TYPES  <- ["NO_FEEDBACK", "AUDIO", "HAPTIC", "BOTH"]
N_ATTEMPTS      = 3;

# command line argument, if present, indicates the results folder
args <- commandArgs(trailingOnly = T)
if (length(args) != 0) {
    res.folder <- args[1]
} else {
    res.folder <- './'
}

# determine whether a string contains a parsable number"
is.number <- function(string) {
    if (length(grep("^[[:digit:]]*$", string)) == 1)
        return (T)
    else
        return (F)
}

# gets the list of files with a certain prefix and suffix in a folder
get.data.files <- function(folder, suffix=".csv") {
    if (strsplit(suffix, '')[[1]][1] == '.')
        suffix <- paste('\\', suffix, sep='')
    return(list.files(folder, pattern=paste('.*', suffix, sep='')))
}

# splits the name of an output file by _ and extracts the values of simulation parameters
get.params <- function(filename, fields) {
    p <- strsplit(gsub(".csv", "", basename(filename)), "_")[[1]]
    #to add a column, we need to have something in the dataframe, so we add a
    #fake column which we remove at the end
    d <- data.frame(todelete=1)
    for (f in 1:length(fields)) {
        v <- p[f]
        if (is.number(v))
            d[[fields[[f]]]] <- as.numeric(v)
        else
            d[[fields[[f]]]] <- v
    }
    d$todelete <- NULL
    return (d)
}

# computes the queue drop rate: dropped packets / generated packets
compute.drop.rate <- function(d, group=F) {
    fields <- c('lambda')
    if (!group)
        fields <- c('src', fields)
    drop.rate <- ddply(d, fields, function(x) {
        all.packets <- subset(x, event == PKT_GENERATED)
        lost.packets <- subset(x, event == PKT_QUEUE_DROPPED)
        return(data.frame(dr=nrow(lost.packets)/nrow(all.packets)))
    }, .parallel=T)
    
  	setAvg <- aggregate(drop.rate$dr, list(drop.rate$lambda), mean)
  	setAvg$dst <- "avg"
  	colnames(setAvg) <- c("lambda", "dr", "src")
  	drop.rate <- rbind(drop.rate, setAvg)
  
    return(drop.rate)
}

# computes corrupted rate: corrupted / (received + corrupted)
compute.corruption.rate <- function(d, group=F) {
    fields <- c('lambda')
    if (!group)
        fields <- c('dst', fields)
    corruption.rate <- ddply(d, fields, function(x) {
        all.packets <- subset(x, event == PKT_RECEIVED | event == PKT_CORRUPTED)
        lost.packets <- subset(all.packets, event == PKT_CORRUPTED)
        return(data.frame(cr=nrow(lost.packets)/nrow(all.packets)))
    }, .parallel=T)
  
  	setAvg <- aggregate(corruption.rate$cr, list(corruption.rate$lambda), mean)
  	setAvg$dst <- "avg"
  	colnames(setAvg) <- c("lambda", "cr", "dst")
  	corruption.rate <- rbind(corruption.rate, setAvg)
  
    return(corruption.rate)
}

# computes collided rate: collided / (received + corrupted)
compute.collision.rate <- function(d, group=F) {
    fields <- c('lambda')
    if (!group)
        fields <- c('dst', fields)
    collision.rate <- ddply(d, fields, function(x) {
        all.packets <- subset(x, event == PKT_RECEIVED | event == PKT_CORRUPTED)
        lost.packets <- subset(x, event == PKT_COLLIDED)
        return(data.frame(cl=nrow(lost.packets)/nrow(all.packets)))
    }, .parallel=T)
  
  	setAvg <- aggregate(collision.rate$cl, list(collision.rate$lambda), mean)
  	setAvg$dst <- "avg"
  	colnames(setAvg) <- c("lambda", "cl", "dst")
  	collision.rate <- rbind(collision.rate, setAvg)
  
    return(collision.rate)
}

# compute throughput: total bits received / simulation time
compute.throughput <- function(d, data.rate, sim.time, group=F) {
    fields <- c('lambda')
    if (!group)
        fields <- c('dst', fields)
    # Count how many seeds were used
    df_uniq <- unique(d$seed)
    seed_number <- length(df_uniq)
    # For each destination and lambda pair, compute the packet received Mbps
    throughput <- ddply(d, fields, function(x) {
        received.packets <- subset(x, event == PKT_RECEIVED)
        return(data.frame(tr=sum(received.packets$size*8)/sim.time/seed_number/(1024**2)))
    }, .parallel=T)
  
  	setAvg <- aggregate(throughput$tr, list(throughput$lambda), mean)
  	setAvg$dst <- "avg"
  	colnames(setAvg) <- c("lambda", "tr", "dst")
  	throughput <- rbind(throughput, setAvg)

    return(throughput)
}

# computes the offered load
compute.offered.load <- function(d, data.rate, sim.time) {
    # keep generation events only
    d <- subset(d, event == PKT_GENERATED)
    offered.load <- ddply(d, c("src", "lambda"), function(x) {
        #return(data.frame(ol=(sum(x$size * 8) / sim.time) / (1024**2)))
    }, .parallel=T)
    return(offered.load)
}

# total offered load in bits per second
offered.load <- function(lambda, n.nodes, packet.size=(1500+32)/2) {
    lambda*n.nodes*packet.size*8/1024/1024
}

## MAIN #################################################################

# if there is no aggregated file, load all csv files into a single one
aggregated.file <- paste(res.folder, 'alld.Rdata', sep='/')
if (!file.exists(aggregated.file)) {
    alld <- data.frame()
    # find all csv in current folder
    data.files <- get.data.files(res.folder, '.csv')
    for (f in data.files) {
        full.path <- paste(res.folder, f, sep='/')
        print(full.path)
        pars <- get.params(full.path, c('prefix', 'lambda', 'seed'))
        d <- read.csv(full.path)
        d <- cbind(d, pars)
        alld <- rbindlist(list(d,alld))
    }
    save(alld, file=aggregated.file)
} else {
    # otherwise simply load the aggregated file
    load(aggregated.file)
}

# get simulation time and number of nodes from the simulation data
sim.time <- max(alld$time)
n.nodes <- length(unique(alld$src))

# compute the statistics
print("Total offered load")
tr <- compute.throughput(alld, 8e6, sim.time)
tr$ol <- offered.load(tr$lambda, n.nodes=n.nodes)

print("Packet corruption rate")
cr <- compute.corruption.rate(alld)
cr$ol <- offered.load(cr$lambda, n.nodes=n.nodes)

print("Packet collision rate")
cl <- compute.collision.rate(alld)
cl$ol <- offered.load(cl$lambda, n.nodes=n.nodes)

print("Packet drop rate")
dr <- compute.drop.rate(alld)
dr$ol <- offered.load(dr$lambda, n.nodes=n.nodes)




## PLOTS 
# and plot the results
div <- 3
text_size <- 20
point_size <- 3
legend_size <- 2

p <- ggplot(tr, aes(x=ol, y=tr, color=factor(dst))) +
        geom_line() +
        geom_point(aes(shape=factor(dst)), size=point_size) +
        scale_shape_manual(values=c(0,1,2,5,6,7,8,9,10,11,20)) +
        xlab('total offered load (Mbps)') +
        ylab('throughput at receiver (Mbps)') +
        labs(color="node", shape="node") +
        theme(text = element_text(size=text_size), legend.key.size = unit(legend_size,"line")) +
        ylim(c(0, 2.5))
ggsave(paste(res.folder, '/thr_', n.nodes, '.pdf', sep=''), width=16/div, height=9/div)
print(p)

pcr <- ggplot(cr, aes(x=ol, y=cr, color=factor(dst))) +
       geom_line() +
       geom_point(aes(shape=factor(dst)), size=point_size) +
       scale_shape_manual(values=c(0,1,2,5,6,7,8,9,10,11,20)) +
       xlab('total offered load (Mbps)') +
       ylab('packet corruption rate at receiver') +
       labs(color="node", shape="node") +
       theme(text = element_text(size=text_size), legend.key.size = unit(legend_size,"line")) +
       ylim(c(0, 1))
ggsave(paste(res.folder, '/pcr_', n.nodes, '.pdf', sep=''), width=16/div, height=9/div)
print(pcr)

pcl <- ggplot(cl, aes(x=ol, y=cl, color=factor(dst))) +
       geom_line() +
       geom_point(aes(shape=factor(dst)), size=point_size) +
       scale_shape_manual(values=c(0,1,2,5,6,7,8,9,10,11,20)) +
       xlab('total offered load (Mbps)') +
       ylab('packet collision rate at receiver') +
       labs(color="node", shape="node") +
       theme(text = element_text(size=text_size), legend.key.size = unit(legend_size,"line")) +
       ylim(c(0, 1))
ggsave(paste(res.folder, '/pcl_', n.nodes, '.pdf', sep=''), width=16/div, height=9/div)
print(pcl)

pdr <- ggplot(dr, aes(x=ol, y=dr, color=factor(src))) +
       geom_line() +
       geom_point(aes(shape=factor(src)), size=point_size) +
       scale_shape_manual(values=c(0,1,2,5,6,7,8,9,10,11,20)) +
       xlab('total offered load (Mbps)') +
       ylab('packet drop rate at sender') +
       labs(color="node", shape="node") +
       theme(text = element_text(size=text_size), legend.key.size = unit(legend_size,"line")) +
       ylim(c(0, 1))
ggsave(paste(res.folder, '/pdr_', n.nodes, '.pdf', sep=''), width=16/div, height=9/div)
print(pdr)
