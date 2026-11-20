/* Bibliographic previews, indexed by the URLs used in the engineering datasets.
   Columns: reference URL, label, local thumbnail, image credit, alternate image source, physics view. */
const EngineeringReferences = (() => {
  const entries = [
    ["https://rotrics.com/pages/dexarm-spec", "Rotrics DexArm tech spec", "ref-00.webp", "Workspace diagram · Rotrics", "", 0],
    ["https://bluerobotics.com/?p=20043", "Blue Robotics R-3318 foam BR-100099", "ref-01.webp", "Machined buoyancy foam · Blue Robotics", "", 0],
    ["https://bluerobotics.com/store/thrusters/t100-t200-thrusters/t200-thruster-r2-rp/", "Blue Robotics T200 thruster", "ref-02.webp", "T200 thruster · Blue Robotics", "", 0],
    ["https://fluxgrip.zubax.com/chapters/hardware/fg40.html", "Zubax FluxGrip FG40 reference manual", "ref-03.webp", "FG401MA magnet · Zubax", "", 0],
    ["https://supermagnete.pt/disc-magnets-neodymium/disc-magnet-20mm-8mm_S-20-08-N", "supermagnete S-20-08-N, N42 D20 x 8", "ref-04.webp", "20 × 8 mm disc magnet · supermagnete", "", 1],
    ["https://core.ac.uk/download/4398847.pdf", "Hennessey 1982, Compliant part mating and minimum energy chamfer design, MIT MS thesis", "ref-05.webp", "Thesis title page · MIT Libraries", "https://dspace.mit.edu/server/api/core/bitstreams/2f87340c-aa4c-46b2-87d0-1b90b826f908/content", 1],
    ["https://www.smooth-on.com/products/sorta-clear-18/", "Smooth-On SORTA-Clear 18", "ref-06.webp", "SORTA-Clear 18 kit · Smooth-On", "", 0],
    ["https://formlabs.com/store/3d-printers/form-4l/", "Formlabs Form 4L store page (build volume)", "ref-07.webp", "Form 4L package · Formlabs", "", 0],
    ["https://www.smooth-on.com/tb/files/DRAGON_SKIN_10_NV_TB.pdf", "Smooth-On Dragon Skin 10 NV technical bulletin", "ref-08.webp", "Technical bulletin, page 1 · Smooth-On", "", 1],
    ["https://www.smooth-on.com/products/dragon-skin-fx-pro/", "Smooth-On Dragon Skin FX-Pro", "ref-09.webp", "Dragon Skin FX-Pro kit · Smooth-On", "", 0],
    ["https://www.nordson.com/products/efd-products/general-purpose-dispense-tips", "Nordson EFD general purpose tips (gauge chart)", "ref-10.webp", "14-gauge dispense tip · Nordson EFD", "", 0],
    ["https://www.pva.net/wp-content/uploads/2022/12/G-Series-Dispense-Needles-12.22.pdf", "PVA G series dispense needles (12G ID 2.16, OD 2.77, Luer lock)", "ref-11.webp", "G-series datasheet, page 1 · PVA", "https://www.pva.net/wp-content/uploads/datasheets/G-Series-Dispense-Needles-12.22.pdf", 0],
    ["https://www.hamiltoncompany.com/knowledge-base/article/needle-gauge-chart", "Hamilton needle gauge chart", "ref-12.webp", "Needle gauge chart · Hamilton", "https://assets-web.hamiltoncompany.com/hamilton-needle-gauge-chart-pdf.pdf?v=1772468034", 0],
    ["https://www.omc-stepperonline.com/nema-23-external-66mm-stack-2-5a-lead-1-5875mm-0-0625-length-150mm-23e26s2504kg-150rs", "StepperOnline 23E26S2504KG, lead 1.5875 mm, 750 N", "ref-13.webp", "Related NEMA 23 external linear actuator · StepperOnline", "https://www.omc-stepperonline.com/nema-23-external-66mm-stack-2-5a-lead-2-54mm-0-1-length-250mm-23e26s2504gg-250rs", 0],
    ["https://www.omc-stepperonline.com/nema-23-external-66mm-stack-2-5a-lead-2-54mm-0-1-length-250mm-23e26s2504gg-250rs", "StepperOnline 23E26S2504GG-250RS, 540 N", "ref-14.webp", "External lead-screw actuator · StepperOnline", "", 0],
    ["https://www.nordson.com/products/efd-products/side-x-side-two-component-cartridges", "Nordson EFD side by side 2K cartridges", "ref-15.webp", "Twin cartridges · Nordson EFD", "", 0],
    ["https://www.ellsworth.com:443/globalassets/literature-library/manufacturer/medmix/medmix-brochure-mixpac-systems-for-adhesives.pdf", "medmix MIXPAC Systems for Adhesives brochure (hosted by Ellsworth)", "ref-16.webp", "MIXPAC brochure cover · medmix", "", 0],
    ["https://lewisgroup.seas.harvard.edu/resource/pdf-24", "Grosskopf et al. 2018, Viscoplastic matrix materials for embedded 3D printing, ACS AMI, doi 10.1021/acsami.7b19818", "ref-17.webp", "Paper, page 1 · Grosskopf et al.", "", 1],
    ["https://s3.amazonaws.com/www.motionusa.com/hiwin/2025/MG%20Series-2025.pdf", "HIWIN MG series catalog (hosted by Motion)", "ref-18.webp", "MG series catalogue page · HIWIN", "", 0],
    ["https://pmc.ncbi.nlm.nih.gov/articles/PMC5740677", "Li, Vogt, Rus, Wood 2017, Fluid-driven origami-inspired artificial muscles, PNAS 114(50):13132, doi:10.1073/pnas.1713450114", "ref-19.webp", "Soft artificial muscle · Wyss Institute", "https://wyss.harvard.edu/technology/foams-soft-robotic-artificial-muscles/", 1],
    ["https://par.nsf.gov/servlets/purl/10295963", "Melancon, Gorissen, Garcia-Mora, Hoberman, Bertoldi 2021, Multistable inflatable origami structures at the metre scale, Nature 592:545, doi:10.1038/s41586-021-03407-4", "ref-20.webp", "Inflatable shelter · Melancon et al.", "https://www.agenciasinc.es/Noticias/Crean-refugios-inflables-inspirados-en-el-origami", 1],
    ["https://journal-scs.symmetry.hu/abstract/?pid=814", "Kresling 2020, The Fifth Fold: complex symmetries in Kresling origami patterns, Symmetry: Culture and Science 31(4):403, doi:10.26830/symmetry_2020_4_403", "ref-21.webp", "Related Kresling model · B. Kresling, 2008", "https://www.academia.edu/38138421/Natural_twist_buckling_in_shells_from_the_hawkmoths_bellows_to_the_deployable_Kresling_pattern_and_cylindrical_Miura_ori", 1],
    ["https://ecommons.cornell.edu/entities/publication/076a6eb3-0d10-46af-a078-3206f67a0c5b", "Kresling 2008, Natural twist buckling in shells: from the hawkmoth bellows to the deployable Kresling pattern and cylindrical Miura-ori, IASS-IACM 2008, Cornell", "ref-22.webp", "Study illustration · B. Kresling", "https://www.academia.edu/38138421/Natural_twist_buckling_in_shells_from_the_hawkmoths_bellows_to_the_deployable_Kresling_pattern_and_cylindrical_Miura_ori", 1],
    ["https://ntrs.nasa.gov/citations/19930093840", "Yoshimura 1955, On the mechanism of buckling of a circular cylindrical shell under axial compression, NACA TM 1390", "ref-23.webp", "Report cover · NACA / NASA archive", "https://ntrs.nasa.gov/api/citations/19930093840/downloads/19930093840.pdf", 1],
    ["https://scispace.com/pdf/self-deployable-origami-stent-grafts-as-a-biomedical-3fsf13bk5l.pdf", "Kuribayashi et al. 2006, Self-deployable origami stent grafts, Mater Sci Eng A 419:131, doi:10.1016/j.msea.2005.12.016", "ref-24.webp", "Stent deployment sequence · Kuribayashi et al.", "https://www.academia.edu/23885658/Self_deployable_origami_stent_grafts_as_a_biomedical_application_of_Ni_rich_TiNi_shape_memory_alloy_foil", 1],
    ["https://escholarship.org/content/qt3nx45751/qt3nx45751.pdf", "Hawkes, Blumenschein, Greer, Okamura 2017, A soft robot that navigates its environment through growth, Science Robotics 2(8):eaan3028, doi:10.1126/scirobotics.aan3028", "ref-25.webp", "Repository cover sheet · UC Santa Barbara", "", 1],
    ["https://acs.figshare.com/articles/journal_contribution/3D_Printing_PDMS_Elastomer_in_a_Hydrophilic_Support_Bath_via_Freeform_Reversible_Embedding/3386209/1", "Hinton, Hudson, Pusch, Lee, Feinberg 2016, 3D printing PDMS elastomer in a hydrophilic support bath via freeform reversible embedding, ACS Biomater Sci Eng, doi:10.1021/acsbiomaterials.6b00170", "ref-26.webp", "Printed silicone structures · Hinton et al.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5059754/", 1],
    ["https://par.nsf.gov/servlets/purl/10085332", "O'Bryan et al. 2017, Self-assembled micro-organogels for 3D printing silicone structures, Science Advances 3:e1602800, doi:10.1126/sciadv.1602800", "ref-27.webp", "Printed silicone scaffold · O’Bryan et al.", "https://www.eurekalert.org/news-releases/923359", 1],
    ["https://dspace.mit.edu/bitstream/handle/1721.1/122801/3dp.2017.0037.pdf?sequence=2", "Hajash, Sparrman, Guberan, Laucks, Tibbits 2017, Large-Scale Rapid Liquid Printing, 3D Printing and Additive Manufacturing 4(3):123, doi:10.1089/3dp.2017.0037", "ref-28.webp", "Printing apparatus · MIT Self-Assembly Lab", "https://selfassemblylab.mit.edu/rapid-liquid-printing/", 1],
    ["https://erikdemaine.org/papers/Hypar_GC/", "Demaine, Demaine, Hart, Price, Tachi 2011, (Non)existence of pleated folds: how paper folds between creases, Graphs and Combinatorics 27(3):377, doi:10.1007/s00373-011-1025-2", "ref-29.webp", "Paper, page 1 · Demaine et al.", "https://erikdemaine.org/papers/Hypar_GC/paper.pdf", 1],
    ["https://ar5iv.arxiv.org/html/0906.4747", "Same paper, full text (circular pleat = concentric circles with a central hole; conjectured to fold without extra creases)", "ref-30.webp", "Folded hypar model · Demaine et al.", "", 1],
    ["https://link.aps.org/doi/10.1103/PhysRevLett.109.114301", "Dias, Dudte, Mahadevan, Santangelo 2012, Geometric mechanics of curved crease origami, PRL 109:114301, doi:10.1103/PhysRevLett.109.114301 (a closed folded crease must buckle out of plane into a saddle)", "ref-31.webp", "Preprint, page 1 · Dias et al.", "https://arxiv.org/pdf/1206.0461", 1],
    ["https://erikdemaine.org/papers/Origamizer_SoCG2017/", "Demaine, Tachi 2017, Origamizer: a practical algorithm for folding any polyhedron, SoCG 2017, LIPIcs 77, 34:1 to 34:16, doi:10.4230/LIPIcs.SoCG.2017.34", "ref-32.webp", "Paper, page 1 · Demaine and Tachi", "https://erikdemaine.org/papers/Origamizer_SoCG2017/paper.pdf", 1],
    ["https://erikdemaine.org/papers/RigidOrigami_JoCG/", "Abel, Cantarella, Demaine, Eppstein, Hull, Ku, Lang, Tachi 2016, Rigid origami vertices: conditions and forcing sets, J Comput Geom 7(1):171, doi:10.20382/jocg.v7i1a9", "ref-33.webp", "Paper, page 1 · Abel et al.", "https://erikdemaine.org/papers/RigidOrigami_JoCG/paper.pdf", 1],
    ["https://erikdemaine.org/papers/Matter_PNAS", "Hawkes, An, Benbernou, Tanaka, Kim, Demaine, Rus, Wood 2010, Programmable matter by folding, PNAS 107(28):12441, doi:10.1073/pnas.0914069107", "ref-34.webp", "Paper, page 1 · Hawkes et al.", "https://erikdemaine.org/papers/Matter_PNAS/paper.pdf", 1],
    ["https://erikdemaine.org/papers/GFALOP/", "Demaine, O'Rourke 2007, Geometric Folding Algorithms: Linkages, Origami, Polyhedra, Cambridge University Press, ISBN 9780521857574", "ref-35.webp", "Book cover · Demaine and O’Rourke", "", 1],
    ["https://arxiv.org/pdf/0711.4664", "Goriely, Destrade, Ben Amar 2006, Instabilities in elastomers and in soft tissues (neo-Hookean balloon pressure peak at stretch 7^(1/6) = 1.38, from Adkins and Rivlin 1952)", "ref-36.webp", "Preprint, page 1 · Goriely et al.", "", 1],
    ["https://ar5iv.labs.arxiv.org/html/2203.04110", "Guo, Wang, Fu 2022, Localised bulging of an inflated rubber tube with fixed ends (bulging starts at the pressure maximum)", "ref-37.webp", "Study plot · Guo, Wang and Fu", "", 1],
    ["https://www.smooth-on.com/tb/files/ECOFLEX_SERIES_TB.pdf", "Smooth-On Ecoflex series technical bulletin: 00-30 SG 1.07, 100 % modulus 10 psi, elongation 900 %, pot life 45 min, cure 4 h; platinum cure inhibitors listed", "ref-38.webp", "Technical bulletin, page 1 · Smooth-On", "", 1],
    ["https://erikdemaine.org/curved/history/", "Demaine, History of Curved Origami Sculpture (Albers 1927-28 concentric circle pleat twists into a saddle)", "ref-39.webp", "Bauhaus folding exercise · Demaine archive", "", 1],
    ["https://physics.uwo.ca/~debruyn/pdfs/j_rheol_2007.pdf", "Tabuteau, Coussot, de Bruyn 2007, Drag force on a sphere in steady motion through a yield-stress fluid, J Rheol 51(1):125, doi:10.1122/1.2401614 (Carbopol; critical Y 0.145, Beris et al. 1985 predict 0.143)", "ref-40.webp", "Paper, page 1 · Tabuteau et al.", "", 1],
    ["https://core.ac.uk/download/43380511.pdf", "Yakubov, Branfield, Bongaerts, Stokes 2015, Tribology of particle suspensions in rolling-sliding soft contacts, Biotribology 3:1 (PDMS on PDMS with aqueous particle suspensions: friction about 0.2 at 1 mm/s)", "ref-41.webp", "Study figure · Yakubov et al.", "", 1],
    ["https://core.ac.uk/download/83983552.pdf", "Selway, Chan, Stokes 2017, Soft Matter 13(8):1702, doi:10.1039/c6sm02417c (notes the high Coulomb friction of PDMS on PDMS)", "ref-42.webp", "Project schematic · Lubricant film between sliding soft surfaces", "", 1],
    ["https://www.lubrizol.com:443/-/media/Lubrizol/Health/Literature/Bulletin-06---Thickening-Properties.pdf", "Lubrizol Pharmaceutical Bulletin 6, Thickening Properties: Carbopol 940 0.5 % at pH 7 about 58,000 cP; soluble salts lower mucilage efficiency", "ref-43.webp", "Project schematic · Carbomer swelling after neutralisation", "", 1],
    ["https://www.mybotshop.de/Datasheet/Datasheet_DexArm_MakerKit.pdf", "DexArm datasheet (MYBOTSHOP, manufacturer specs): repeatability 0.05 mm, precision 0.1 mm, payload 500 g, max print speed 150 mm/s, 2.4 kg", "ref-44.webp", "DexArm specification sheet · MYBOTSHOP", "", 1],
    ["https://researchspace.auckland.ac.nz/handle/2292/40216?show=full", "Peristaltic actuation of the canal sleeve · Auckland research repository", "ref-45.webp", "Project schematic · Sequential constriction in a peristaltic sleeve", "", 1],
    ["https://par.nsf.gov/servlets/purl/10085335", "Bhattacharjee et al. (2015). Writing in the granular gel medium.", "ref-46.webp", "Granular-gel printing · Bhattacharjee et al., 2015", "https://phys.org/news/2015-09-gels-unique.html", 1],
    ["https://par.nsf.gov/servlets/purl/10432202", "Zhong et al. (2023). EpoMemory: Multi-state Shape Memory for Programmable Morphing Interfaces.", "ref-47.webp", "Shape-memory octopus prototype · Morphing Matter Lab", "https://morphingmatter.org/projects/epomemory", 1],
    ["https://manual.rotrics.com/product-overview/product-profile", "Rotrics DexArm manual · positioning repeatability", "ref-48.webp", "DexArm working envelope · Rotrics", "https://rotrics.com/pages/dexarm-spec", 1],
    ["https://www.smooth-on.com/tb/files/DRAGON_SKIN_FX_PRO_TB.pdf", "Smooth-On Dragon Skin FX-Pro technical bulletin (100 % modulus 37.8 psi, elongation 763 %)", "ref-49.webp", "Technical bulletin, page 1 · Smooth-On", "", 1],
    ["https://doi.org/10.1063/1.1712836", "Mooney 1940, A theory of large elastic deformation, J Appl Phys 11:582, doi:10.1063/1.1712836", "ref-50.webp", "Project schematic · Uniaxial extension of an incompressible elastic specimen", "", 1],
    ["https://doi.org/10.1098/rsta.1948.0024", "Rivlin 1948, Large elastic deformations of isotropic materials IV, Phil Trans R Soc A 241:379, doi:10.1098/rsta.1948.0024", "ref-51.webp", "Project schematic · Simple shear of an elastic block", "", 1],
    ["https://doi.org/10.1098/rsta.1952.0013", "Adkins and Rivlin 1952, Large elastic deformations of isotropic materials IX: thin shells, Phil Trans R Soc A 244:505, doi:10.1098/rsta.1952.0013", "ref-52.webp", "Project schematic · Pressure acting on a thin curved shell", "", 1],
    ["https://doi.org/10.1093/imamat/36.1.85", "Pipkin 1986, The relaxed energy density for isotropic elastic membranes, IMA J Appl Math 36:85, doi:10.1093/imamat/36.1.85", "ref-53.webp", "Project schematic · Wrinkling of an elastic membrane", "", 1],
    ["https://doi.org/10.1017/S0022112085002622", "Beris, Tsamopoulos, Armstrong, Brown 1985, Creeping motion of a sphere through a Bingham plastic, J Fluid Mech 158:219, doi:10.1017/S0022112085002622", "ref-54.webp", "Journal cover · Cambridge University Press", "", 1],
    ["https://doi.org/10.1007/BF01591800", "Eason and Shield 1960, The plastic indentation of a semi-infinite solid by a perfectly rough circular punch, ZAMP 11, doi:10.1007/BF01591800 (N_c 6.05; original not opened)", "ref-55.webp", "Project schematic · Flat circular punch pressing into a solid half-space", "", 1],
    ["https://doi.org/10.1016/0377-0257(81)80024-9", "Covey and Stanmore 1981, Use of the parallel-plate plastometer for the characterisation of viscous fluids with a yield stress, J Non-Newt Fluid Mech 8:249, doi:10.1016/0377-0257(81)80024-9", "ref-56.webp", "Related squeeze-flow apparatus · NETZSCH", "https://analyzing-testing.netzsch.com/en/application-literature/using-squeeze-flow-to-extend-rheological-measurements-for-concentrated-suspensions", 1],
    ["https://knf.com/fileadmin/Global_files/Downloads/Product_OEM_Process/Datasheets/DB_NMP830.X_EN_28112023.pdf", "KNF NMP830 datasheet (5.6 L/min free flow, 1.5 bar)", "ref-57.webp", "NMP 830 datasheet, page 1 · KNF", "https://knf.com/fileadmin/Global_files/Downloads/Product_OEM_Process/Datasheets/DB_NMP830_EN_05062025.pdf", 1],
    ["https://www.astm.org/d1894-14.html", "ASTM D1894, coefficient of friction of plastic film", "ref-58.webp", "ASTM D1894 friction sled · Mecmesin", "https://www.mecmesin.com/accessory/432-638", 1],
    ["https://doi.org/10.1089/3dp.2017.0037", "Hajash et al. 2017, Large-Scale Rapid Liquid Printing", "ref-59.webp", "Rapid Liquid Printing · MIT Self-Assembly Lab", "https://selfassemblylab.mit.edu/rapid-liquid-printing/", 1],
    ["https://knf.com/en/us/solutions/pumps/series/diaphragm-gas-pump-nmp-830", "KNF diaphragm pump data", "ref-60.webp", "NMP 830 pump · KNF", "", 1],
    ["https://formlabs.com/tds/clear-resin-v5-tds", "Formlabs Clear Resin V5 TDS", "ref-61.webp", "Clear Resin V5 datasheet · Formlabs", "https://formlabs-media.formlabs.com/filer_public/dd/7f/dd7f3de9-55ae-4c82-ac52-408a4b5df64d/clear_resin_v5_tds___formlabs.pdf", 0],
    ["https://multimedia.3m.com/mws/media/2522968O/3m-scotch-weld-epoxy-adhesive-dp100-plus-clear.pdf", "3M Scotch-Weld DP100 Plus Clear TDS", "ref-62.webp", "DP100 Plus datasheet · 3M", "", 0],
    ["https://www.parker.com/content/dam/Parker-com/Literature/O-Ring-Division-Literature/ORD-5700.pdf", "Parker O-Ring Handbook ORD 5700", "ref-63.webp", "Handbook cover · Parker", "", 0],
    ["https://www.smooth-on.com/products/ecoflex-00-30/", "Smooth-On Ecoflex 00-30", "ref-64.webp", "Ecoflex 00-30 kit · Smooth-On", "", 0],
    ["https://elegoo.com/products/orangestorm-giga", "Elegoo OrangeStorm Giga", "ref-65.webp", "OrangeStorm Giga printer · Elegoo", "", 0],
    ["https://www.omc-stepperonline.com/nema-17-bipolar-59ncm-84oz-in-2a-42x48mm-4-wires-w-1m-cable-connector-17hs19-2004s1", "StepperOnline 17HS19-2004S1", "ref-66.webp", "NEMA 17 motor · StepperOnline", "", 0],
    ["https://www.rotrics.com/products/dexarm", "Rotrics DexArm product page", "ref-67.webp", "DexArm and accessories · Rotrics", "", 0],
    ["https://bluerobotics.com/store/comm-control-power/powersupplies-batteries/battery-li-4s-18ah/", "Blue Robotics 14.8 V 18 Ah battery BR-100842", "ref-68.webp", "Lithium-ion battery pack · Blue Robotics", "", 0],
    ["https://www.raspberrypi.com/products/raspberry-pi-5/", "Raspberry Pi 5", "ref-69.webp", "Raspberry Pi 5 board · Raspberry Pi", "", 0],
    ["https://global.bttwiki.com/SKR%20Pico.html", "BIGTREETECH SKR Pico wiki", "ref-70.webp", "SKR Pico board dimensions · BIGTREETECH", "", 0],
    ["https://bluerobotics.com/?p=28583", "Blue Robotics stainless ballast 200 g BR-101039", "ref-71.webp", "Stainless ballast weight · Blue Robotics", "", 0],
    ["https://www.flashforge.com/products/adventurer-5m-3d-printer", "Flashforge Adventurer 5M", "ref-72.webp", "Adventurer 5M printer · Flashforge", "", 0],
    ["https://www.bbraunusa.com/en/products/b0/three-way-stopcockwithspin-lock.html", "B. Braun three way stopcock D300, REF 456003", "ref-73.webp", "Stopcock diagram · B. Braun", "", 0],
    ["https://docs.google.com/presentation/d/1fTm_oDPefzafITs2w75gJIZ8zdXcw0acMDKE9GcqqMM", "Artist's Weekly Updates deck (S8 design, gel tests)", "ref-74.webp", "Project presentation title slide · Born, Not Made", "", 0],
    ["https://github.com/TheRobotStudio/SO-ARM100", "TheRobotStudio · SO-100 and SO-101 open robot arms", "ref-75.webp", "SO-101 follower arm · TheRobotStudio", "", 0],
    ["https://www.clippard.com/part/EV-2-12", "Clippard EV-2-12", "ref-76.webp", "EV-2-12 valve · Clippard", "", 0],
    ["https://www.bosch-sensortec.com/products/environmental-sensors/pressure-sensors/bmp390/", "Bosch Sensortec BMP390", "ref-77.webp", "BMP390 sensor · Bosch Sensortec", "", 0],
    ["https://www.lubrizol.com/Personal-Care/Products/Product-Finder/Products-Data/Carbopol-940-polymer", "Lubrizol Carbopol 940 polymer", "ref-78.webp", "Project schematic · Crosslinked polymer network in a swollen carbomer particle", "", 0],
    ["https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5059754/fullTextXML", "Hinton et al. 2016, doi 10.1021/acsbiomaterials.6b00170 (Europe PMC full text)", "ref-79.webp", "Printed silicone structures · Hinton et al.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5059754/", 0],
    ["https://docs.google.com/presentation/d/1gDGtGLfvkKU6tBiIV1BffReg0fe-eCJgThqy-QIFMio", "Baby Robots Material Fabrication Updates (gel recipe)", "ref-80.webp", "Related prototype photograph · Born, Not Made", "../#prototypes", 0],
    ["https://www.smooth-on.com/products/ecoflex-00-35/", "Smooth-On Ecoflex 00-35 (FAST data)", "ref-81.webp", "Ecoflex 00-35 FAST kit · Smooth-On", "", 0],
    ["https://shop.zubax.com/products/zubax-epm", "Zubax FluxGrip FG40 shop page", "ref-82.webp", "FG40 pole face · Zubax", "", 0],
    ["https://www.mill-max.com/products/datasheet/0906-2-15-20-75-14-11-0", "Mill-Max 0906-2-15-20-75-14-11-0 datasheet", "ref-83.webp", "0906 spring contact · Mill-Max / DigiKey", "https://www.digikey.com/en/products/detail/mill-max-manufacturing-corp/0906-2-15-20-75-14-11-0/1147050", 0],
    ["https://patents.google.com/patent/US8579744B2/en", "US8579744B2, inflation valve core for sports balls", "ref-84.webp", "Patent drawing · pneumatic inflation valve", "https://www.patentsencyclopedia.com/imgfull/20120058846_05", 0],
    ["https://microbots.io/products/codecell-c6-drive", "microbots CodeCell C6 Drive", "ref-85.webp", "CodeCell C6 Drive · Microbots", "", 0],
    ["https://core-electronics.com.au/mute-sounds-mini-submersible-pump-dc-3v-5v.html", "Core Electronics mini submersible pump (reseller, no primary exists)", "ref-86.webp", "Mini submersible pump · Core Electronics", "", 0],
    ["https://github.com/RealManRobot/ros2_rm_robot/tree/711abedd48c6614f26fb4f7661db92f306ff05bd/rm_description", "RealMan ECO62 robot description and link meshes", "ref-87.webp", "Related ECO62-B six-axis arm · Robot Digest", "https://www.robot-digest.com/contents/?id=1731906131-288421", 0]
  ];
  const byUrl = new Map(entries.map(entry => [entry[0], entry]));

  function link(label, href) {
    const anchor = document.createElement("a");
    anchor.textContent = label;
    anchor.href = href;
    anchor.target = "_blank";
    anchor.rel = "noopener";
    return anchor;
  }

  function render(container, sources, physicsOnly = false, component = false) {
    const items = new Map(sources);
    if (!component) {
      for (const [url, title] of entries) if (!items.has(url)) items.set(url, title);
    }
    const cards = document.createDocumentFragment();
    for (const [url, label] of items) {
      const entry = byUrl.get(url);
      if (physicsOnly && entry && !entry[5]) continue;
      const item = document.createElement("li");
      if (entry) {
        const [, title, file, credit, imageSource] = entry;
        const photo = link("", imageSource || url);
        photo.className = "eng-image";
        const image = document.createElement("img");
        image.src = "../assets/img/engineering/" + file;
        image.alt = credit;
        image.loading = "lazy";
        image.decoding = "async";
        photo.append(image);
        const titleLink = link(component ? label : title, url);
        titleLink.className = "eng-title";
        const creditLink = link(credit, imageSource || url);
        creditLink.className = "eng-credit";
        item.append(photo, titleLink, creditLink);
      } else {
        item.append(link(label, url));
      }
      cards.append(item);
    }
    container.classList.add("engineering-references");
    if (component) container.classList.add("engineering-compact");
    container.replaceChildren(cards);
  }

  return { render };
})();
