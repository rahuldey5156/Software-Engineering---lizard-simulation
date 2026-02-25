'''Lizard-insect-berry simulation.

Version 1.0, last updated in Feb 2026.
'''
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import math
import numpy as np
import random

def getVersion():
    return 1.0

def simCommLineIntf():
    par=ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    par.add_argument("-b","--berry-prop",type=float,default=0.05,help="Approximate proportion of landscape filled with berries")
    par.add_argument("-c","--berry-growth",type=float,default=0.001,help="Approximate proportion of berries that appears each timestep")
    par.add_argument("-i","--insect-prop",type=float,default=0.08,help="Approximate proportion of landscape filled with insects")
    par.add_argument("-j","--insect-move-ts",type=int,default=5,help="Timesteps for insect movements")
    par.add_argument("-l","--lizard-prop",type=float,default=0.01,help="Approximate proportion of landscape filled with lizards")
    par.add_argument("-m","--lizard-move-ts",type=int,default=2,help="Timesteps for lizard movements")
    par.add_argument("-n","--lizard-view-radius",type=int,default=3,help="Maximum number of cells lizards watch for insects")
    par.add_argument("-o","--output-ts",type=int,default=10,help="Number of time steps at which to output files")
    par.add_argument("-x","--cutoff",type=int,default=500,help="Maximum time to run the simulation (in timesteps)")
    par.add_argument("-f","--landscape-file",type=str,required=True,
                        help="Input landscape file")
    par.add_argument("-s","--seed",type=int,default=1,help="Random seed for initialising locations and movement")
    args=par.parse_args()
    sim(args.berry_prop,args.berry_growth,args.insect_prop,args.insect_move_ts,args.lizard_prop,args.lizard_move_ts,args.lizard_view_radius,args.output_ts,args.cutoff,args.landscape_file,args.seed)

def sim(b,c,i,j,l,m,n,o,co,lfile,seed):
    print("Insect simulation",getVersion())
    with open(lfile,"r") as f:
        w,h=[int(v) for v in f.readline().split(" ")]
        print("Width: {} Height: {}".format(w,h))
        wh=w+2 # Width including halo
        hh=h+2 # Height including halo
        lscape=np.zeros((hh,wh),int)
        row=1
        for line in f.readlines():
            values=line.split(" ")
            # Read landscape into array,padding with halo values.
            lscape[row]=[0]+[int(v) for v in values]+[0]
            row += 1

    its=np.zeros((hh,wh),int)
    random.seed(seed)
    for x in range(1,h+1):
        for y in range(1,w+1):
            if lscape[x,y]:
                r=random.random()
                if r<b:
                    its[x,y]=1

                r=random.random()
                if r<i:
                    its[x,y]=2
    
                r=random.random()
                if r<l:
                    its[x,y]=3
    
    # Create copies of initial maps and arrays for PPM file maps.
    # Reuse these so we don't need to create new arrays going
    # round the simulation loop.
    its_nu=its.copy()
    with open("averages.csv","w") as f:
        hdr="Timestep,# Fruit,# Insects,Avg distance to berry,# Lizards, Avg distance to insect\n"
        f.write(hdr)

    for t in range(0,co):
        if t%o == 0:
            bpos=[]
            ipos=[]
            lpos=[]
            for x in range(1,h+1):
                for y in range(1,w+1):
                    if lscape[x,y]:
                        if its[x,y]==1:
                            bpos+=[(x,y)]
                        if its[x,y]==2:
                            ipos+=[(x,y)]
                        if its[x,y]==3:
                            lpos+=[(x,y)]
                        
            nb=len(bpos)
            ni=len(ipos)
            nl=len(lpos)

            idis=[]
            ldis=[]
            for ip in ipos:
                mindis=math.inf
                for bp in bpos:
                    dis=abs(ip[0]-bp[0])+abs(ip[1]-bp[1])
                    if dis < mindis:
                        mindis=dis
                idis+=[mindis]
            for lp in lpos:
                mindis=math.inf
                for ip in ipos:
                    dis=abs(lp[0]-ip[0])+abs(lp[1]-ip[1])
                    if dis < mindis:
                        mindis=dis
                ldis+=[mindis]
            ai=sum(idis)/len(idis) if idis else math.inf
            al=sum(ldis)/len(ldis) if ldis else math.inf
            print("Averages. Timestep: {} Berries: {} Insects: {}({:.3f}) Lizards: {}({:.3f})".format(t,nb,ni,ai,nl,al))
            with open("averages.csv","a") as f:
                f.write("{},{},{},{:.3f},{},{:.3f}\n".format(t,nb,ni,ai,nl,al))
            bcols=np.zeros((h,w),int)
            icols=np.zeros((h,w),int)
            lcols=np.zeros((h,w),int)
            for x in range(1,h+1):
                for y in range(1,w+1):
                    if lscape[x,y]:
                        if its[x,y]==1:
                            bcols[x-1,y-1]=150
                        elif its[x,y]==2:
                            icols[x-1,y-1]=150
                        elif its[x,y]==3:
                            lcols[x-1,y-1]=200
                            dirs=[(-1,0),(1,0),(0,-1),(0,1)]
                            q=[]
                            vis=set((x,y))
                            for dx,dy in dirs:
                                cx=x+dx
                                cy=y+dy
                                if lscape[cx,cy]:
                                    q+=[(cx,cy,dx,dy,1)]
                            while q:
                                cx,cy,odx,ody,d=q.pop(0)
                                if (cx,cy) in vis:
                                    continue
                                if d > n:
                                    continue
                                vis.add((cx,cy))
                                lcols[cx-1,cy-1]=max(lcols[cx-1,cy-1],100 / d)
                                for dx,dy in dirs:
                                    nx,ny=cx+dx,cy+dy
                                    if lscape[nx,ny] and (nx,ny) not in vis:
                                        q.append((nx,ny,odx,ody,d+1))
            with open("map_{:04d}.ppm".format(t),"w") as f:
                hdr="P3\n{} {}\n{}\n".format(w,h,255)
                f.write(hdr)
                for x in range(0,h):
                    for y in range(0,w):
                        if lscape[x+1,y+1]:
                            f.write("{} {} {}\n".format(bcols[x,y],lcols[x,y],icols[x,y]))
                        else:
                            f.write("{} {} {}\n".format(0,200,255))

        for x in range(1,h+1):
            for y in range(1,w+1):
                its_nu[x,y]=its[x,y]

        for x in range(1,h+1):
            for y in range(1,w+1):
                if lscape[x,y] and not its[x,y]:
                    r=random.random()
                    if r<c:
                        its_nu[x,y]=1

        if t%j == 0:
            for x in range(1,h+1):
                for y in range(1,w+1):
                    if its[x,y] == 2:
                        idirs=[(-1,0),(1,0),(0,-1),(0,1)]
                        dirs=[]
                        while idirs:
                            idx=math.floor(random.random() * len(idirs))
                            dirs+=[idirs.pop(idx)]
                        q=[]
                        vis=set((x,y))
                        fnd=False
                        for dx,dy in dirs:
                            cx=x+dx
                            cy=y+dy
                            if lscape[cx,cy]:
                                q+=[(cx,cy,dx,dy)]
                        while q and not fnd:
                            cx,cy,odx,ody=q.pop(0)
                            if (cx,cy) in vis:
                                continue
                            vis.add((cx,cy))
                            if its[cx,cy] == 1:
                                fnd=True
                                break
                            for dx,dy in dirs:
                                nx,ny=cx+dx,cy+dy
                                if lscape[nx,ny] and (nx,ny) not in vis:
                                    q.append((nx,ny,odx,ody))
                        if fnd:
                            nx,ny=x+odx,y+ody
                        if not fnd or its[nx,ny] in (2,3) or its_nu[nx,ny] in (2,3):
                            nx,ny=x,y
                        its_nu[x, y] = 0
                        its_nu[nx, ny] = 2
        
        if t%m == 0:
            for x in range(1,h+1):
                for y in range(1,w+1):
                    if its[x,y] == 3:
                        idirs=[(-1,0),(1,0),(0,-1),(0,1)]
                        dirs=[]
                        while idirs:
                            idx=math.floor(random.random() * len(idirs))
                            dirs+=[idirs.pop(idx)]
                        q=[]
                        vis=set((x,y))
                        fnd=False
                        for dx,dy in dirs:
                            cx=x+dx
                            cy=y+dy
                            if lscape[cx,cy]:
                                q+=[(cx,cy,dx,dy,1)]
                        while q and not fnd:
                            cx,cy,odx,ody,d=q.pop(0)
                            if (cx,cy) in vis:
                                continue
                            if d > n:
                                continue
                            vis.add((cx,cy))
                            if its[cx,cy] == 2:
                                fnd=True
                                break
                            for dx,dy in dirs:
                                nx,ny=cx+dx,cy+dy
                                if lscape[nx,ny] and (nx,ny) not in vis:
                                    q.append((nx,ny,odx,ody,d+1))
                        if fnd:
                            nx,ny=x+odx,y+ody
                        if not fnd or its[nx,ny] in (1,3) or its_nu[nx,ny] in (1,3):
                            nx,ny=x,y
                        its_nu[x, y] = 0
                        its_nu[nx, ny] = 3

        # Swap arrays for next iteration.
        tmp=its
        its=its_nu
        its_nu=tmp
        

if __name__ == "__main__":
    simCommLineIntf()
