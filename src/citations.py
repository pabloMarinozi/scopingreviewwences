import scholar as sch

phrase = "Early detection of grapevine leafroll disease in a red-berried wine grape cultivar using hyperspectral imaging"

#Le quitamos la ultima letra
link = sch.scholar(phrase[:-1])
print(link)