# SubShift

Proportionally subtitles shifting from one timestamps offset and rate to another.  
Heavily used by https://vk.com/teamnotdead releases.

Usage: subshift.py shift.cfg, where shift.cfg structure is:

source.srt  
target.srt  
n1	NewTimeStamp1 (hh:mm:ss,ms or hh:mm:ss.ms)  
...  
nK	NewTimeStampK  
