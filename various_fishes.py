hello_world = r'''
"hello, world!"r\
           o;!?l<
'''[1:-1]


fizzbuzz = r'''
0voa                            ~/?=0:\
 voa            oooo'Buzz'~<     /
 >1+:aa*1+=?;::5%:{3%:@*?\?/'zziF'oooo/
 ^oa                 n:~~/
 '''[1:-1]


fibonacci = r'''
10::n' 'o&+&$10.
'''[1:-1]


lucas = r'''
2n' 'ol?/21>::!
    $&+&\  /
'''[1:-1]


factorial = r'''
 :?\~11>*l1\
-1:/ ;n\?- /
'''[1:-1]


quine1 = r'''
"r00gol?!;40.
'''[1:-1]


sqrt = r'''
1[:>:r:@@:@,\;
]~$\!?={:,2+/n
'''[1:-1]


quine2 = r'''
0>:a$f8+$p1+:5-?vv     
 ^              <>~0v  
v             <     <  
>0v          ;^?-6:+1~<
v <                  < 
>$:{:}$go$   1+:f9+-?^^
'''[1:-1]


bf = r'''
v
1
0

           >$    >$                 \
>:@$:@i:0(?^$:2=?^$:3b*-0=?\v/      >:&$:1=?v>$@p&0(?v$1+
\                  02]p00~~<> :'+'=?^\      $$       >1-0p
\01-\                       /^?='>': <      d+
v   <}            v?= \     > :'<'=?^\      %e
v}]p$p4r}:r:$4[2@:/f1+/     /^?='-': <      \/
>{1+:00g=?\:1g:e-?^~:}0a.   > :'['=?^\
/     -1-:/                 /^?=']': <
>1+:00g=?;:1g0$.            > :'.'=?^\
^             ~<   $\.51$~~ ~^?=',': <
 '['~ 20g:3g  ?^>$4g^

 ']'~ 20g:3g0=?^^
^                 <     \
 '+'~ 20g:3g1+3$@p^
 ','~ 30g:1+30p2g  20g3p/
 '-'~ 20g:3g1-3$@p^
 '.'~ 20g3go      /
 '<'~ 20g1-20p\
^             <
 '>'~ 20g1+20p/
'''[1:-1]

# should return '1'
move1 = r'''
v
1
>?v 1n;\
 0<    /
'''[1:-1]

# should return 'Hi'
move2 = r'''
aa*5+\
7a*2+\
oo;  \
'''[1:-1]

# should return the input reversed
tac = r'''
i:1+?!v
      ~
l?!;o >
'''[1:-1]

# should return '\n'.join(map(str, range(100))) + '\n'
range100 = r'''
01+:aa*=?;:nao!
'''[1:-1]

# should throw an error if not ROUND_VALUES and return '' otherwise
fracjump = r'''
b2,63,.

   17,n;
'''[1:-1]

collatz = r'''
i>:nao:1=?;\
 ^  ,2v?%2:/
 ^+1*3<
'''[1:-1]

draweq = r'''
a&>i:0(?v"+"$\
/&^?=0l< "a*"/
\:1+&2p/\0
n
;
'''[1:-1]