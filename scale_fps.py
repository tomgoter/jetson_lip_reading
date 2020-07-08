#
import sys, os, argparse

parser = argparse.ArgumentParser()
parser.add_argument('-d', "--directory", help="Path to images to edit", required=True)
parser.add_argument('--fps', type=int, choices=[10,15], help="Desired Output FPS", required=True)
parser.add_argument('--down', type = bool, help="Are we reducing the number of images")
args = parser.parse_args()

print(args.down)

file_list = os.listdir(args.directory)

file_ids = [int(x.split('.')[0]) for x in file_list if x[-3:] == 'jpg']

sorted_ids = sorted(file_ids)

counter = 0
stopper = 30 / args.fps
print(f"Keeping one image of every {stopper}")
for s, id in enumerate(sorted_ids):
    if id>9999: break
    if args.down:
        if counter == 0:
            print(f"Keeping image {id}")
            os.system(f'cp {args.directory}/{id}.jpg {args.directory}/{20000+int(id/stopper)}.jpg')
            counter += 1
        elif counter == stopper-1:
            counter = 0
            continue
    else:
        if counter == 0:
            for c in range(int(stopper)):
                print(f"Keeping image {id}")
                os.system(f'cp {args.directory}/{id}.jpg {args.directory}/{10000+s+c}.jpg')
            
        elif counter == stopper-1:
            counter = 0  
            continue     
    counter += 1
  
  