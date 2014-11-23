substations = \

{
's0' : {'name': 'raceway' },
's1' : {'name': 'pinnacle_peak_aps' },
's2' : {'name': 'lone_peak'},
's3' : {'name': 'pinnacle_peak_walc'},
's4' : {'name': 'gavilan_peak'},
's5' : {'name': 'westwing'},
's6' : {'name': 'perkins'},
's7' : {'name': 'surprise'},
's8' : {'name': 'el_sol'},
's9' : {'name': 'agua_fria'},
's10' : {'name': 'deer_valley'},
's11' : {'name': 'alexander'},
's12' : {'name': 'glendale'},
's13' : {'name': 'sunny_slope'},
's14' : {'name': 'meadowbrook'},
's15' : {'name': 'country_club'},
's16' : {'name': 'lincoln'},
's17' : {'name': 'west_phoenix'},
's18' : {'name': 'white_tanks_aps'},
's19' : {'name': 'white_tanks_srp'},
's20' : {'name': 'rudd'},
's21' : {'name': 'orme'},
's22' : {'name': 'anderson'},
's23' : {'name': 'liberty'},
's24' : {'name': 'buckeye'},
's25' : {'name': 'lone_butte'},
's26' : {'name': 'test_track'},
's27' : {'name': 'duke'},
's28' : {'name': 'santa_rosa'},
's29' : {'name': 'desert_basin'},
's30' : {'name': 'casa_grande'},
's31' : {'name': 'milligan'},
's32' : {'name': 'sundance'},
's33' : {'name': 'coolidge'},
's34' : {'name': 'valley_farms'},
's35' : {'name': 'randolph'},
's36' : {'name': 'hayden'},
's37' : {'name': 'abel'},
's38' : {'name': 'dinosaur'},
's39' : {'name': 'browning'},
's40' : {'name': 'santan'},
's41' : {'name': 'schrader'},
's42' : {'name': 'kyrene'},
's43' : {'name': 'knox'},
's44' : {'name': 'ward'},
's45' : {'name': 'brandow'},
's46' : {'name': 'ocotillo'},
's47' : {'name': 'corbell'},
's48' : {'name': 'cactus'},
's49' : {'name': 'pinnacle_peak_srp'},
's50' : {'name': 'rogers'},
's51' : {'name': 'goldfield'},
's52' : {'name': 'thunderstone'},
's53' : {'name': 'papago_buttes'}
}

lines = {}

s0 ?
s0 ?
s0 s1
s0 s5

s1 ?
s1 ?
s1 ?
#s1 s0
s1 s2
s1 s3
s1 s46
s1 s49

#s2 s1
s2 s13

s3 ?
s3 ?
#s3 s1
s3 s4
s3 s5
s3 s49
s3 s50
s3 s50

s4 ?
#s4 s3

s5 ?
s5 ?
s5 ?
s5 ?
s5 ?
#s5 s0
#s5 s3
s5 s6
s5 s7
s5 s9
s5 s10
s5 s23

s6 ?
#s6 s5

#s7 s5
s7 s8

#s8 s7
s8 s9
s8 s20

#s9 s5
#s9 s8
s9 s11
s9 s12
s9 s19

s10 s11
s10 s12
s10 s49

#s11 s9
#s11 s10

#s12 s9
s12 s15

#s13 s2
s13 s11

#s14 s13
s14 s15

#s15 s12
#s15 s14
s15 s16

#s16 s15
s16 s17
s16 s46

#s17 s16
s17 s18
s17 s20
s17 s23
s17 s25

#s18 s8
#s18 s17
s18 s20

#s19 s9
s19 s20

s20 ?
#s20 s17
#s20 s18
#s20 s19
s20 s21
s20 s23

#s21 s20
s21 s22

#s22 s21
s22 s42

s23 ?
s23 ?
s23 ?
#s23 s5
#s23 s17
#s23 s20
s23 s24
s23 s25

s24 ?
#s24 s23

#s25 s17
#s25 s23
s25 s26
s25 s32

#s26 s25
s26 s58
s26 s30

s27 ?
s27 ?

s28 ?
#s28 s25
s28 s29
s28 s43

s29 ?
s29 ?
#s29 s28

#s30 s26
s30 s31

s31 ?
#s31 s30

#s32 s25
s32 s33

s33 ?
s33 ?
#s33 s32
s33 s34

s34 ?
#s34 s33

s35 ?
s35 s37

s36 ?

#s37 s35
s37 s38

#s38 s37
s38 s39

s39 ?
s39 ?
#s39 s38
s39 s40
s39 s42

#s40 s39
s40 s41
s40 s47
s40 s52

#s41 s40
s41 s42

s42 ?
s42 s43
#s42 s22
s42 s46
s42 s53
s42 s45
#s42 s39
s42 s47
#s42 s41

#s43 s28
#s43 s42

s44 s45

#s45 s42
#s45 s44
s45 s49
s45 s53

#s46 s1
#s46 s16
#s46 s42

#s47 s40
#s47 s42

s48 s1?
s48 s46?

#s49 s1
#s49 s3
#s49 s10
#s49 s45
s49 s53

#s50 s3
#s50 s3
s50 s52
#s50 s33

s51 ?
s51 s52

#s52 s40
#s52 s50
#s52 s51

#s53 s42
#s53 s45
#s53 s49
