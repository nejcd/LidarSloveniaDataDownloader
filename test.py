#!/usr/bin/env python

import getLSS as lss

#http://gis.arso.gov.si/lidar/dmr1/b_31/D48GK/GK1_441_136.asc


tile = [441, 136, 31] 
CRS = 'D48GK' 
product = 'OTR(laz) '
destination = '/Users/nejc/Downloads'


if product == 'OTR(zlas)':
    productname = 'OTR'
    extension = 'zlas'
    fileprefix = 'R'
elif product == 'OTR(laz) ':
    productname = 'OTR/laz'
    extension = 'laz'
    fileprefix = 'R'
elif product == 'GKOT(zlas)':
    productname = 'GKOT'
    extension = 'zlas'
    fileprefix = ''
elif product == 'GKOT(laz) ':
    productname = 'GKOT/laz'
    extension = 'laz'
    fileprefix = ''
elif product == 'DMR':
    productname = product
    extension = 'asc'
    fileprefix = '1'


[tileE, tileN, block_number] = tile
filename = '{0}{1}_{2}_{3}.{4}'.format(CRS[-2:], fileprefix, tileE, tileN, extension)
print 'Testing: ' + filename

lss.getLSSrequests(tile, CRS, product, destination)