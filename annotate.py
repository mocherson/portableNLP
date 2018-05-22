import re
import pandas as pd


alias_lists = [
    ['Asthma', ],   # asztma
    ['CAD',         # szívkoszorúér betegség [elmeszesedés]
#        'coronary (?:(?:artery|heart)? ?disease|atherosclerosis)',
#        'coronary (?:atherosclerosis)',  # remove is better
        'coronary angioplasty',
        'Percutaneous coronary intervention',
        'PCI', # FIXME intuitive
        'Atherosclerotic disease',
        'chd',
        'coronary artery bypass',
        'coronary artery disease' #added
#        'LAD',
        ],
    ['CHF',         # kongesztív szívbetegség
        '(?:congestive )?(?:heart|cardiac) failure',
        'CCF',
        'dchf',
        '(?:dilated|(?:non-?)?ischa?emic) cardiomyopathy',
#       'cardiomyopathy',
#		'CMP',
#        'Pulmonary edema',
        ],
    ['Depression',                                # depresszió
        'depressive?',
        ],
    ['Diabetes',                                    # cukorbetegség
        'DM',
        'N?IDDM',  # = diabetes mellitus
        'diabetic',
         ],
    ['Gallstones',                                  # epekő (nem betegség
        'gall ?stones?',
        'Cholelithiasis',
#        'pancreatitis', # NOTE epekő következménye
        'biliary colic', # NOTE tünet
        'Cholecystectomy', # NOTE műtét
        'Gallbladder removal',  # NOTE műtét
        'CCY',
        'gallbladder (?:[a-z-\/]+ )*stones',
#        'pancreatic duct',
        #,'Cholestasis', # NOTE epekő következménye
        ],
    ['GERD',                                        # reflux
        'reflux (?:disease|disorder|esophagitis)',
        '(?:gastro(?:-o)?)?esophageal reflux',
        'G-?E Reflux',
        'gord',
        's esophagitis', # barretts's esophagitis
#        'reflux',
        ],
    ['Gout',
    	'gouty',
        'metabolic arthritis',
	],                    # köszvény
    ['Hypercholesterolemia',                        # hypercholesterinaemia
        'hyperchol\w*',
        '(?:high|elev(?:ated)?|increased) (?:chol(?:esterol)?|lipids?)',
        '(?:chol(?:esterol)?|lipids?)(?:\w|-| )+(?:high|elev(?:ated)?|increased)',
#         'hyperlipi?demia',   # NOTE utal rá
#         'hyperlipoproteinemia' , # NOTE utal rá
#         'dyslipidemia', # NOTE általánosabb
        'hyperli?pi?d\w*',   # NOTE utal rá
#        'hyperlipoproteinemia' , # NOTE utal rá
#        'dyslipidemia', # NOTE általánosabb
        'dysli?pi?d\w+', # NOTE általánosabb

        ],
    ['Hypertension',                                # magasvérnyomás
        'htn',
#       'elevated bp',
        ],
    ['Hypertriglyceridemia',                        # u.a.
        'Hyper(?:tri)?glycerid[a-z]*',
        'hyper tg',
        '(?:high|elev(?:ated)?|increased) trig(?:lyceride)?s',
        't(?:g|rig(?:lyceride)?s?) (?:[a-z0-9\-\/]+ )*(?:high|elev(?:ated)?|increased)',
        ],
    ['OA',                                  # rheumatoid arthritis
        '(?:Osteo)?arthritis',
        'degenerative (arthritis|joint disease)',
        'DJD',
        ],
    ['Obesity',                                   # elhízás
        'obes\w+',
#       'weight gain', # tul sok FP
        ],
    ['OSA',
        '(obstructive )?sleep apnea', ],           # alvási apnoe [horkolás]
    ['PVD', # Végtagi érelmeszesedés [verőérszűkület]
        'Peripheral (?:vascular|arterial)(?: occlusive)? Disease',
        'peripherovascular disease',
#        'peripheral arterial disease',
#        'PAD',
        ],
    ['Venous Insufficiency',       #visszér betegség
        'venostasis',   # NOTE alfaj
        '(veno)?stasis dermatitis',   # NOTE alfaj
        'venous (?:stasis|return)',
        ],
        
];

# lowercase!
# no active parens '(' in regex! only '(?:' allowed
fake_aliases = {
    'Depression' : [
        'resp(?:iratory)? depr[a-z]*',
        's(?:t|cd) (?:segment )?depr[a-z]*',
        ],
    'Diabetes' : [
	'(?:gestional|chemical) diabetes',
	'diabetic diet',
	],

    'OA' : [
        '(?:rheumatoid|septic|psoriatic|idiopathic) arthritis',
        'oa7'
        ],
    'Asthma' : [
#        'asthma flare',
        'cardiac asthma',
        ],
    'Hypertension' : [
    	'pulmonary hypertension',
    	],
    	
};

intuitive_alias_lists =[
    [ 'Depression' ,
        '(?:prozac|zoloft|wellbutrin|plaxil|lexapro|effexor|cymbalta|elavil|celexa|desyrel|Pamelor|Tofranil)',
        '(?:ssri|snri)s?',
        'antidepressants?',
        ],
    [ 'Hypertension',
        '(?:ACE inhibitors|antihypertensive)s?',
        '(?:Angiotensin|b(?:eta)?(?: |-)blocker)',
         '(blood pressure|bp)( of | )(1[4-9][0-9]|[2-9]\d{2,})/(9[0-9]|[1-9]\d{2,})'
        ],
    [ 'GERD',
        'ESOPHAGITIS',
        '(?:carafate|Sucralfate)',
        
        ],

   [ 'CAD',
        'Cardiac catheterization',
        ],
    [ 'Hypercholesterolemia',
        '[a-z]+statins?',
        ],
#     [ 'Hypertriglyceridemia',
#         'fibrates?',
#        '(?:Bezafibrate|Bezalip|Ciprofibrate|Modalim|Clofibrate|Gemfibrozil|Lopid|Fenofibrate|Tricor)',
#         ],
    [ 'Obesity',
        'Pannicul(?:ectomy|itis)',
        ],
    [ 'OA',
        'LUMBAR DIS[kc] DISEASE',
        'hip replacement',
        'knee replacement',
        ],
    [ 'Gout',
        'Allopurinol',
        ],
    [ 'Venous Insufficiency',
        '(?:lower extremity|leg) ulcers',
        ],
#     [ 'Hypertriglyceridemia',
#         'hyperglycerida?emia',   # NOTE általánosabb
#         ],

];

fake_negatives = (
	'gram negative',
	'no further',
	'not able to be',
    'no increase',
    'not suspicious',
	'not certain',
	'not clearly',
	'not certain whether',
	'not certain if',
	'not necessarily',
	'not optimal',
	'not rule out',
	'without any further',
	'without difficulty',
	'without further',
	'not correlate',
	'no correlataion',
	
#'no family history', # unstripped family history segments
	'no prior',
);

alias_lists = alias_lists+intuitive_alias_lists
aliases={}
for dis in alias_lists:
    tag = dis[0]
    for alias in dis:
        alias = alias.lower()
        alias = re.sub(' ','[ _]',alias)
        aliases[alias] = tag


def findQpos(doc):
    line=re.finditer(r'((?:(?:\b(?:not certain if|versus|vs|rule out|be ruled out|r\/o|presumed|suggest(?:\b|[^i]|i[^v])|possib|scree?n for|question|consider|whether or not|may have|study for))(?:[^\.\,;:)(\?]+))|\?(?: ?[a-z\/\-]+){1,4}|(?:[a-z\-\/]+ )+(?:versus|vs|screen)[a-z -]+)', doc.lower())
    fea_sen = [(x.span(),x.group(0)) for x in line]
    fea = pd.DataFrame(columns=['disease','dis_pos','dis_alias','sen_pos','sentence','tail'])
#     print(fea_sen)
    for sen in fea_sen:
        s = sen[1]
        pos = sen[0]
        tail = ''
        if not re.search(r'(?:versus|vs|screen)',sen[1]):
            rs=re.search(r'^(.+?)((?:\b(?:no |and|when|with|given|if|besides|because|related|component|from|since|secondary|regard|due|disposing)\b|\b-\B|\B-\b|\-\-|\*\*).*)',s)
            if rs:
                s = rs.group(1)
                pos = [x+pos[0] for x in rs.span(1)]
                tail = rs.group(2)
#         print(s)
        for alias, tag in aliases.items():
            fake = '(?:' + '|'.join(fake_aliases[tag]) + ')|' if tag in fake_aliases else ''
            match_dis = re.finditer(r'(?:'+fake+r'(?:\b|[0-9])('+alias+r')(?:\b|[0-9]))',s)  
            fea_words = [(dis.span(),dis.group(0)) for dis in match_dis if dis.group(1)]
            for f in fea_words:
                fea.loc[len(fea)] = [tag,f[0],f[1],sen[0],sen[1],tail]   
        doc = doc[:pos[0]]+' '*(pos[1]-pos[0])+doc[pos[1]:]
#         print(pos,s)
    return fea, doc

def findNpos(doc):
    line=re.finditer(r'(\b(?:no|not|denie[sd]|denying|rule[sd] out|neg(?:ative)?|w(?:ithout|-\B|\/o\b)|did not exhibit|declined|(?:\w|\s|-)+ neg(?:ative)?) (?:[^\.\,\;\:\)\(\?\*]+)|non-[a-z-]+)', doc.lower())
    fea_sen = [(x.span(),x.group(0)) for x in line]
    fea = pd.DataFrame(columns=['disease','dis_pos','dis_alias','sen_pos','sentence','tail'])
    for sen in fea_sen:
        s = sen[1]
        pos = sen[0]
        tail = ''
        blk=' '*(pos[1]-pos[0])
        rs=re.search(r'((?:\b(?:when|given|taken|takes?|from|further|but|taking|during|as|besides|more|who|after|complications? of|because|since|due to|unless|regarding|secondary)\b|\b-\B|\B-\b|\-\-|\*\*).*)',s)
        if rs:
            tail=rs.group(1)
            tpos=rs.span(1)
            s=re.sub(r'((?:\b(?:when|given|taken|takes?|from|further|but|taking|during|as|besides|more|who|after|complications? of|because|since|due to|unless|regarding|secondary)\b|\b-\B|\B-\b|\-\-|\*\*).*)','',s)            
            blk = blk[:tpos[0]]+tail+blk[tpos[1]:]
#         print(s,tail)
        if any([re.search(fake,s) for fake in fake_negatives]):
            continue
            
        for alias, tag in aliases.items():
            fake = '(?:' + '|'.join(fake_aliases[tag]) + ')|' if tag in fake_aliases else ''
            match_dis = re.finditer(r'('+fake+r'(?:\b|[0-9])('+alias+r')(?:\b|[0-9]))',s) 
            fea_words = [(dis.span(),dis.group(0)) for dis in match_dis if dis.group(2)]
            for f in fea_words:
                fea.loc[len(fea)] = [tag,f[0],f[1],sen[0],sen[1],tail]
        
        doc = doc[:pos[0]]+blk+doc[pos[1]:]
    return fea,doc

def findPpos(doc):
    fea = pd.DataFrame(columns=['disease','dis_pos','dis_alias'])
    for alias, tag in aliases.items():
        fake = '(?:' + '|'.join(fake_aliases[tag]) + ')|' if tag in fake_aliases else ''
        match_dis = re.finditer(r'('+fake+r'(?:\b|[0-9])('+alias+r')(?:\b|[0-9]))',doc.lower())
#         print('('+fake+r'(?:\b|[0-9])('+alias+r')(?:\b|[0-9]))')
#         print([(x.group(0),x.group(1),x.group(2)) for x in match_dis])
        fea_words = [(dis.span(),dis.group(0)) for dis in match_dis if dis.group(2)]
        for f in fea_words:
            fea.loc[len(fea)] = [tag,f[0],f[1]]
    return fea
    
corp_name='Obesity_data/ObesitySen_remove_familiy_history.dms'
f = open(corp_name,'r')
content = f.read()
f.close()
records = content.strip().split('RECORD #')    
for i in range(1,1250):
	print('processing the %dth document'%(i))
	Qfea,doc=findQpos(records[i])
	Qfea.to_csv('featurepos/Question/Qpos_%d.csv'%(i))
	Nfea,doc=findNpos(doc)
	Nfea.to_csv('featurepos/Negated/Npos_%d.csv'%(i))
	Pfea=findPpos(doc)
	Pfea.to_csv('featurepos/Positive/Ppos_%d.csv'%(i))

