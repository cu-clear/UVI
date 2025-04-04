var generateDiagram = document.querySelector('.btn');
var currentEvent = id;

// generateDiagram.addEventListener('click', draw);


function resetScreen() {

    var resetDiv = document.querySelectorAll('.svg-diagram');
    for (var i = 0 ; i < resetDiv.length ; i++) {
        resetDiv[i].textContent = '';
    }

    var resetText = document.querySelectorAll('.textbox');
    for (var i = 0 ; i < resetText.length ; i++) {
        resetText[i].textContent = '';
    }   

    draw();

}

function addSecondDivText (myText, bold=true, n) {

    if (n%2!==0) {element = "textbox_right"}
        else {element = "textbox_left"}

    var theDiv = document.getElementById(element);
    var h2 = document.createElement("H2");
    var vn_element = document.createElement("vn_element")
    var content = document.createTextNode(myText);

    if (bold==true) {
        theDiv.appendChild(h2);
        h2.appendChild(content);
    } else {

        if (n===6) {
            var cell = document.getElementById("textbox");
            cell.appendChild(content);
        }

        else {

            if (n === 0 || n === 1 || n === 3){
                theDiv.appendChild(vn_element);
                vn_element.appendChild(content);
            }

            else {

            theDiv.appendChild(content);

            }
        
        }

    }

}

// the event representations


var events = {
    "1000": [
        "Herman spliced ropes",
        "shake-22.3-2-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Internal",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,ropes) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "1001": [
        "Linda taped the label and the cover together",
        "tape-22.4",
        "Sbj V Obj",
        "NP V NP together",
        "Volitional Internal",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Linda) & Component-of(b,label and the cover) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "1002": [
        "The dog flopped in the corner",
        "assuming_position-50",
        "Sbj V LocP",
        "NP V PP.location",
        "Autonomous Location",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,dog) & Component-of(b,corner) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1003": [
        "Italy borders France",
        "contiguous_location-47.8",
        "Sbj V Obj",
        "NP V NP",
        "Autonomous Location",
        "InherentState",
        "Theme-of(x,e) & Component-of(a,Italy) & Component-of(b,France) & InhStPh(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1004": [
        "A fire raged in the mountains",
        "entity_specific_modes_being-47.2",
        "Sbj V LocP",
        "NP V PP.location",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,fire) & Component-of(b,mountains) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1005": [
        "All through the mountains raged a fire",
        "entity_specific_modes_being-47.2",
        "Sbj V LocP",
        "NP.location V NP",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,fire) & Component-of(b,mountains) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1006": [
        "Herbicides persist in the soil",
        "exist-47.1",
        "Sbj V LocP",
        "NP V PP.location",
        "Autonomous Location",
        "TransitoryState",
        "Theme-of(x,e) & Component-of(a,Herbicides) & Component-of(b,soil) & TranStPh(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1007": [
        "There sparkled a magnificent diamond on his finger",
        "light_emission-43.1",
        "Sbj V LocP",
        "There V NP PP.location",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,diamond) & Component-of(b,finger) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1008": [
        "Jewels sparkled on the crown",
        "light_emission-43.1",
        "Sbj V LocP",
        "NP V PP.location",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Jewels) & Component-of(b,crown) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1009": [
        "On his finger there sparkled a magnificent diamond",
        "light_emission-43.1",
        "Sbj V LocP",
        "PP.location there V NP",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,diamond) & Component-of(b,finger) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1010": [
        "Through the valley meanders the river",
        "meander-47.7",
        "Sbj V LocP",
        "PP.location V NP",
        "Autonomous Location",
        "InherentState",
        "Theme-of(x,e) & Component-of(a,river) & Component-of(b,valley) & InhStPh(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1011": [
        "There meanders a river through the valley",
        "meander-47.7",
        "Sbj V LocP",
        "There V NP PP",
        "Autonomous Location",
        "InherentState",
        "Theme-of(x,e) & Component-of(a,river) & Component-of(b,valley) & InhStPh(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1012": [
        "There meanders through the valley a river",
        "meander-47.7",
        "Sbj V LocP",
        "There V PP NP",
        "Autonomous Location",
        "InherentState",
        "Theme-of(x,e) & Component-of(a,river) & Component-of(b,valley) & InhStPh(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1013": [
        "A flag fluttered over the fort",
        "modes_of_being_with_motion-47.3",
        "Sbj V LocP",
        "NP V PP.location",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,flag) & Component-of(b,fort) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1014": [
        "Over the fort fluttered a flag",
        "modes_of_being_with_motion-47.3",
        "Sbj V LocP",
        "PP.location V NP",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,flag) & Component-of(b,fort) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1015": [
        "A serious accident happened in front of them",
        "occur-48.3",
        "Sbj V LocP",
        "NP V PP",
        "Autonomous Location",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,accident) & Component-of(b,them) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1016": [
        "In the hallway ticked a grandfather clock",
        "sound_emission-43.2",
        "Sbj V LocP",
        "PP.location V NP",
        "Autonomous Location",
        "CyclicAchievement",
        "Theme-of(x,e) & Component-of(a,clock) & Component-of(b,hallway) & CycAch(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1017": [
        "There ticked a grandfather clock in the hallway",
        "sound_emission-43.2",
        "Sbj V LocP",
        "There V NP PP",
        "Autonomous Location",
        "CyclicAchievement",
        "Theme-of(x,e) & Component-of(a,clock) & Component-of(b,hallway) & CycAch(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1018": [
        "Horns beeped in the street",
        "sound_emission-43.2",
        "Sbj V LocP",
        "NP V PP.location",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Horns) & Component-of(b,street) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1019": [
        "There echoed voices through the hall",
        "sound_existence-47.4",
        "Sbj V LocP",
        "There V NP",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,voices) & Component-of(b,hall) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1020": [
        "The voices echoed through the hall",
        "sound_existence-47.4",
        "Sbj V LocP",
        "NP V PP.location",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,voices) & Component-of(b,hall) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1021": [
        "Through the hall echoed a loud cry",
        "sound_existence-47.4",
        "Sbj V LocP",
        "PP.location V NP",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,cry) & Component-of(b,hall) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1022": [
        "On the pedestal stood a statue",
        "spatial_configuration-47.6",
        "Sbj V LocP",
        "PP.location V NP",
        "Autonomous Location",
        "TransitoryState",
        "Theme-of(x,e) & Component-of(a,statue) & Component-of(b,pedestal) & TranStPh(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1023": [
        "The statue stood on the corner",
        "spatial_configuration-47.6",
        "Sbj V LocP",
        "NP V PP.location",
        "Autonomous Location",
        "TransitoryState",
        "Theme-of(x,e) & Component-of(a,statue) & Component-of(b,corner) & TranStPh(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1024": [
        "There stood on the corner a statue",
        "spatial_configuration-47.6",
        "Sbj V LocP",
        "There V PP NP",
        "Autonomous Location",
        "TransitoryState",
        "Theme-of(x,e) & Component-of(a,statue) & Component-of(b,corner) & TranStPh(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1025": [
        "There bubbled a fragrant stew over the fire",
        "substance_emission-43.4-1",
        "Sbj V LocP",
        "There V NP PP",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,stew) & Component-of(b,fire) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1026": [
        "Over the fire bubbled a fragrant stew",
        "substance_emission-43.4-1",
        "Sbj V LocP",
        "PP.location V NP",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,stew) & Component-of(b,fire) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1027": [
        "Bees are swarming in the garden",
        "swarm-47.5.1-1",
        "Sbj V LocP",
        "NP V PP.location",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Bees) & Component-of(b,garden) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1028": [
        "There swarm bees in the garden",
        "swarm-47.5.1-1",
        "Sbj V LocP",
        "There V NP PP",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,bees) & Component-of(b,garden) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1029": [
        "In the aquarium swam a striped fish",
        "swarm-47.5.1-1",
        "Sbj V LocP",
        "PP.location V NP",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,fish) & Component-of(b,aquarium) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1030": [
        "There abound flowers in the garden",
        "swarm-47.5.1-2",
        "Sbj V LocP",
        "There V NP PP",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,flowers) & Component-of(b,garden) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1031": [
        "Flowers abound in the garden",
        "swarm-47.5.1-2",
        "Sbj V LocP",
        "NP V PP.location",
        "Autonomous Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Flowers) & Component-of(b,garden) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1032": [
        "We camped there",
        "lodge-46",
        "Sbj V LocP",
        "NP V ADV",
        "Self-volitional Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,We) & Component-of(b,there) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1033": [
        "Cornelia lodged with the Stevensons",
        "lodge-46",
        "Sbj V with Obl",
        "NP V PP.location",
        "Self-volitional Location",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Cornelia) & Component-of(b,Stevensons) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & INT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1034": [
        "The plane landed",
        "pocket-9.10-1",
        "Sbj V",
        "NP V",
        "Autonomous Motion",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,plane) & Component-of(b,NI) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1035": [
        "The ball rolled",
        "roll-51.3.1",
        "Sbj V",
        "NP.theme V",
        "Autonomous Motion",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,ball) & Component-of(b,NI) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1036": [
        "The book slid",
        "slide-11.2",
        "Sbj V",
        "NP V",
        "Autonomous Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,book) & Component-of(b,NI) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1037": [
        "The rope curled upward",
        "coil-9.6-1",
        "Sbj V PathP",
        "NP V ADV-Middle",
        "Autonomous Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,rope) & Component-of(b,upward) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1038": [
        "The boat sailed across the lake",
        "nonvehicle-51.4.2-1",
        "Sbj V PathP",
        "NP V PP",
        "Autonomous Motion",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,boat) & Component-of(b,lake) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1039": [
        "The ball rolled down the hill",
        "roll-51.3.1",
        "Sbj V PathP",
        "NP V PP.location",
        "Autonomous Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,ball) & Component-of(b,hill) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1040": [
        "The book slid from the table",
        "slide-11.2",
        "Sbj V PathP",
        "NP V PP.initial_location",
        "Autonomous Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,book) & Component-of(b,table) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1041": [
        "The book slid from the table to the floor",
        "slide-11.2",
        "Sbj V PathP",
        "NP V PP.initial_location PP.destination",
        "Autonomous Motion",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,books) & Component-of(b,table-floor) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1042": [
        "The books slid to the floor",
        "slide-11.2",
        "Sbj V PathP",
        "NP V PP.destination",
        "Autonomous Motion",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,books) & Component-of(b,floor) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1043": [
        "Water gushed through the streets",
        "substance_emission-43.4-1",
        "Sbj V PathP",
        "NP V PP.location",
        "Autonomous Motion",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Water) & Component-of(b,streets) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1044": [
        "The water seeped out",
        "substance_emission-43.4-1",
        "Sbj V PathP",
        "NP V out",
        "Autonomous Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,water) & Component-of(b,out) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1045": [
        "Oil gushed from the well",
        "substance_emission-43.4-1",
        "Sbj V PathP",
        "NP.theme V PP.source",
        "Autonomous Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,Oil) & Component-of(b,well) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1046": [
        "Claire took a train from Reno",
        "vehicle_path-51.4.3",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location",
        "Facilitating Motion",
        "DirectedAchievement",
        "N/A & Component-of(a,Claire) & Component-of(b,train) & Component-of(c,Reno) & N/A & VOL(q1) & MOT(q1) & FAC(a,b) & PTH(a,c)"
    ],
    "1047": [
        "Jack took a flight to Tuscon",
        "vehicle_path-51.4.3",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Facilitating Motion",
        "DirectedAchievement",
        "N/A & Component-of(a,Jack) & Component-of(b,flight) & Component-of(c,Tuscon) & N/A & VOL(q1) & MOT(q1) & FAC(a,b) & PTH(a,c)"
    ],
    "1048": [
        "The train brought us here",
        "bring-11.3",
        "Sbj V Obj PathP",
        "NP V NP ADVP",
        "Physical Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,train) & Component-of(b,us) & Component-of(c,here) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1049": [
        "They rowed",
        "nonvehicle-51.4.2",
        "Sbj V",
        "NP.agent V",
        "Self-volitional Motion",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,They) & Component-of(b,NI) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1050": [
        "The horse jumped",
        "run-51.3.2",
        "Sbj V",
        "NP V",
        "Self-volitional Motion",
        "CyclicAchievement",
        "Theme-of(x,e) & Component-of(a,horse) & Component-of(b,NI) & CycAch(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1051": [
        "Claire skated",
        "vehicle-51.4.1",
        "Sbj V",
        "NP.theme V",
        "Self-volitional Motion",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Claire) & Component-of(b,NI) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1052": [
        "They waltzed",
        "waltz-51.5",
        "Sbj V",
        "NP.theme V",
        "Self-volitional Motion",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,They) & Component-of(b,NI) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1053": [
        "He came from France to Colorado",
        "escape-51.1",
        "Sbj V PathP",
        "NP V PP.initial_loc PP.destination",
        "Self-volitional Motion",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,He) & Component-of(b,Colorado) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1054": [
        "He came through the door",
        "escape-51.1",
        "Sbj V PathP",
        "NP V PP.trajectory",
        "Self-volitional Motion",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,He) & Component-of(b,door) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1055": [
        "He came to Colorado",
        "escape-51.1",
        "Sbj V PathP",
        "NP V PP.destination",
        "Self-volitional Motion",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,He) & Component-of(b,Colorado) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1056": [
        "The prisoners advanced",
        "escape-51.1-1",
        "Sbj V",
        "NP V",
        "Self-volitional Motion",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,prisoners) & Component-of(b,NI) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1057": [
        "He came from France",
        "escape-51.1-1",
        "Sbj V PathP",
        "NP V PP.initial_loc",
        "Self-volitional Motion",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,He) & Component-of(b,France) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1058": [
        "The convict escaped the prison",
        "escape-51.1-1-1",
        "Sbj V Obj",
        "NP V NP",
        "Self-volitional Motion",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,convict) & Component-of(b,prison) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1059": [
        "He entered the room",
        "escape-51.1-1-2",
        "Sbj V Obj",
        "NP V NP",
        "Self-volitional Motion",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,He) & Component-of(b,room) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1060": [
        "He climbed the mountain",
        "escape-51.1-1-3",
        "Sbj V Obj",
        "NP V NP",
        "Self-volitional Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,He) & Component-of(b,mountain) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1062": [
        "The crowd left",
        "leave-51.2-1",
        "Sbj V",
        "NP V",
        "Self-volitional Motion",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,crowd) & Component-of(b,NI) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1063": [
        "They rowed the canals of Venice",
        "nonvehicle-51.4.2",
        "Sbj V Obj",
        "NP V NP.location",
        "Self-volitional Motion",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,They) & Component-of(b,canals) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1064": [
        "They rowed along the canal",
        "nonvehicle-51.4.2",
        "Sbj V PathP",
        "NP V PP.location",
        "Self-volitional Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,They) & Component-of(b,canal) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1065": [
        "I landed there",
        "pocket-9.10-1",
        "Sbj V PathP",
        "NP V ADVP",
        "Self-volitional Motion",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,I) & Component-of(b,there) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1066": [
        "I landed in Russia",
        "pocket-9.10-1",
        "Sbj V PathP",
        "NP V PP.destination",
        "Self-volitional Motion",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,I) & Component-of(b,Russia) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1067": [
        "They reached the hill",
        "reach-51.8",
        "Sbj V Obj",
        "NP V NP",
        "Self-volitional Motion",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,They) & Component-of(b,hill) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1068": [
        "There jumped out of the box a little white rabbit",
        "run-51.3.2",
        "Sbj V PathP",
        "There V PP NP",
        "Self-volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,rabbit) & Component-of(b,box) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1069": [
        "Out of the box jumped a little white rabbit",
        "run-51.3.2",
        "Sbj V PathP",
        "PP.location V NP",
        "Self-volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,rabbit) & Component-of(b,box) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1070": [
        "The horse jumped over the fence",
        "run-51.3.2",
        "Sbj V PathP",
        "NP V PP.location",
        "Self-volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,horse) & Component-of(b,fence) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1071": [
        "There jumped a little white rabbit out of the box",
        "run-51.3.2",
        "Sbj V PathP",
        "There V NP PP",
        "Self-volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,rabbit) & Component-of(b,box) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1072": [
        "The horse traveled the stream",
        "run-51.3.2-1",
        "Sbj V Obj",
        "NP V NP",
        "Self-volitional Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,horse) & Component-of(b,stream) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1073": [
        "The horse jumped the stream",
        "run-51.3.2-2-1",
        "Sbj V Obj",
        "NP V NP",
        "Self-volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,horse) & Component-of(b,stream) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1074": [
        "Gordo took an unknown route from Topeka",
        "vehicle_path-51.4.3",
        "Sbj V PathP",
        "NP V NP PP.initial_location",
        "Self-volitional Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,Gordo) & Component-of(b,Topeka) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1075": [
        "Martha took the back way to Nederland",
        "vehicle_path-51.4.3",
        "Sbj V PathP",
        "NP V NP PP.destination",
        "Self-volitional Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,Martha) & Component-of(b,Nederland) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1076": [
        "Kevin took the freeway",
        "vehicle_path-51.4.3",
        "Sbj V PathP",
        "NP V NP",
        "Self-volitional Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,Kevin) & Component-of(b,freeway) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1077": [
        "Claire skated along the canal",
        "vehicle-51.4.1",
        "Sbj V PathP",
        "NP.theme V PP.location",
        "Self-volitional Motion",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,Claire) & Component-of(b,canal) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1078": [
        "Claire skated the canals",
        "vehicle-51.4.1-1",
        "Sbj V Obj",
        "NP V NP",
        "Self-volitional Motion",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Claire) & Component-of(b,canals) & UndAct(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1079": [
        "They waltzed across the room and into the hallway",
        "waltz-51.5",
        "Sbj V PathP",
        "NP V PP.trajectory PP.goal",
        "Self-volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,They) & Component-of(b,hallway) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & MOT(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1080": [
        "Bill rolled the ball",
        "roll-51.3.1",
        "Sbj V Obj",
        "NP V NP.theme",
        "Volitional Motion",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Bill) & Component-of(b,ball) & Component-of(c,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1081": [
        "Jackie accompanied Rose to the store",
        "accompany-51.7",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Jackie) & Component-of(b,Rose) & Component-of(c,store) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1082": [
        "The king deported the general to the isle",
        "banish-10.2",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,king) & Component-of(b,general) & Component-of(c,isle) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1083": [
        "Nora brought the book",
        "bring-11.3",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Nora) & Component-of(b,book) & Component-of(c,NI) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1084": [
        "Nora brought the book from home to the meeting",
        "bring-11.3",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location PP.destination",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Nora) & Component-of(b,book) & Component-of(c,meeting) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1085": [
        "Nora brought the book to the meeting",
        "bring-11.3",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Nora) & Component-of(b,book) & Component-of(c,meeting) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1086": [
        "Nora brought the book from home",
        "bring-11.3",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Nora) & Component-of(b,book) & Component-of(c,home) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1087": [
        "Nora brought to lunch the book",
        "bring-11.3",
        "Sbj V Obj PathP",
        "NP V PP.destination NP",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Nora) & Component-of(b,book) & Component-of(c,lunch) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1088": [
        "Amanda carried the package",
        "carry-11.4",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Motion",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,package) & Component-of(c,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1089": [
        "Amanda carried the package from home",
        "carry-11.4",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,package) & Component-of(c,home) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1090": [
        "Amanda carried the package to New York",
        "carry-11.4",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,package) & Component-of(c,York) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1091": [
        "Amanda carried the package from home to New York",
        "carry-11.4",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location PP.destination",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,package) & Component-of(c,York) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1092": [
        "Amanda carried the package to New York from home",
        "carry-11.4",
        "Sbj V Obj PathP",
        "NP V NP PP.destination PP.initial_location",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,package) & Component-of(c,home) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1093": [
        "Amanda shoved the box",
        "carry-11.4-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,box) & Component-of(c,NI) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1094": [
        "Amanda shoved the box from the corner",
        "carry-11.4-1",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,box) & Component-of(c,corner) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1095": [
        "Jackie chased the thief down the street",
        "chase-51.6",
        "Sbj V Obj PathP",
        "NP V NP PP.location",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Jackie) & Component-of(b,thief) & Component-of(c,street) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1096": [
        "Amanda drove the package",
        "drive-11.5",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Motion",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,package) & Component-of(c,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1097": [
        "Amanda drove the package to New York",
        "drive-11.5",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,package) & Component-of(c,York) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1098": [
        "Amanda drove the package from home",
        "drive-11.5",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,package) & Component-of(c,home) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1099": [
        "Amanda drove Penny to New York from home",
        "drive-11.5",
        "Sbj V Obj PathP",
        "NP V NP PP.destination PP.initial_location",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,Penny) & Component-of(c,home) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1100": [
        "Amanda drove the package from home to New York",
        "drive-11.5",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location PP.destination",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,package) & Component-of(c,York) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1101": [
        "Amanda shuttled her children",
        "drive-11.5-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Motion",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,children) & Component-of(c,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1102": [
        "Amanda shuttled her children from Philadelphia",
        "drive-11.5-1",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,children) & Component-of(c,Philadelphia) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1103": [
        "Amanda shuttled the children to school",
        "drive-11.5-1",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,children) & Component-of(c,school) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1104": [
        "Amanda trucked the package from Philadelphia to her mother's house",
        "drive-11.5-1",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location PP.destination",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,package) & Component-of(c,Philadelphia-house) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1105": [
        "Amanda trucked the package to her mother's house from Philadelphia",
        "drive-11.5-1",
        "Sbj V Obj PathP",
        "NP V NP PP.destination PP.initial_location",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Amanda) & Component-of(b,package) & Component-of(c,Philadelphia-house) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1106": [
        "He rowed the boat across the lake",
        "nonvehicle-51.4.2",
        "Sbj V Obj PathP",
        "NP V NP PP.location",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,boat) & Component-of(c,lake) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1107": [
        "I lifted the books",
        "put_direction-9.4",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,books) & Component-of(c,NI) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1108": [
        "Bill rolled the ball down the hill",
        "roll-51.3.1",
        "Sbj V Obj PathP",
        "NP V NP PP.location",
        "Volitional Motion",
        "DirectedActivity",
        "Theme-of(y,e) & Component-of(a,Bill) & Component-of(b,ball) & Component-of(c,hill) & UndAct(a,i,j,q1) & DirAct(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1109": [
        "Tom jumped the horse",
        "run-51.3.2-2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Tom) & Component-of(b,horse) & Component-of(c,NI) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1110": [
        "Tom jumped the horse over the fence",
        "run-51.3.2-2",
        "Sbj V Obj PathP",
        "NP V NP PP.location",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Tom) & Component-of(b,horse) & Component-of(c,fence) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1111": [
        "The lion tamer jumped the lions",
        "run-51.3.2-2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,lion tamer) & Component-of(b,lions) & Component-of(c,NI) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1112": [
        "The lion tamer jumped the lions through the loop",
        "run-51.3.2-2",
        "Sbj V Obj PathP",
        "NP V NP PP.location",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,lion tamer) & Component-of(b,lions) & Component-of(c,loop) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1113": [
        "Nora sent the book",
        "send-11.1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Nora) & Component-of(b,book) & Component-of(c,NI) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1114": [
        "Nora sent the book from Paris",
        "send-11.1",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Nora) & Component-of(b,book) & Component-of(c,Paris) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1115": [
        "Nora sent the book to London",
        "send-11.1",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Nora) & Component-of(b,book) & Component-of(c,London) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1116": [
        "Nora sent the book from Paris to London",
        "send-11.1",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location PP.destination",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Nora) & Component-of(b,book) & Component-of(c,London) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1117": [
        "Carla slid the books",
        "slide-11.2",
        "Sbj V Obj",
        "NP.agent V NP",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Carla) & Component-of(b,books) & Component-of(c,NI) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1118": [
        "Carla slid the books across the table",
        "slide-11.2",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Carla) & Component-of(b,books) & Component-of(c,table) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1119": [
        "Carla slid the books from one end of the table to the other",
        "slide-11.2",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location PP.destination",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Carla) & Component-of(b,books) & Component-of(c,other) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1120": [
        "Carla slid the books to the floor",
        "slide-11.2",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Carla) & Component-of(b,books) & Component-of(c,floor) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1121": [
        "Jessica squirted water",
        "spray-9.7",
        "Sbj V Obj",
        "NP V NP.theme",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Jessica) & Component-of(b,water) & Component-of(c,NI) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1122": [
        "Steve tossed the ball",
        "throw-17.1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Steve) & Component-of(b,ball) & Component-of(c,NI) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1123": [
        "I threw the package away",
        "throw-17.1",
        "Sbj V Obj",
        "NP V NP ADVP",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,package) & Component-of(c,NI) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1124": [
        "Steve tossed the ball from the corner to the garden",
        "throw-17.1",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location PP.destination",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Steve) & Component-of(b,ball) & Component-of(c,garden) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1125": [
        "Steve tossed the ball to the garden",
        "throw-17.1",
        "Sbj V Obj PathP",
        "NP V NP PP.destinations",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Steve) & Component-of(b,ball) & Component-of(c,garden) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1126": [
        "Steve tossed the ball from the corner",
        "throw-17.1",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location",
        "Volitional Motion",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Steve) & Component-of(b,ball) & Component-of(c,corner) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1127": [
        "He skated Penny",
        "vehicle-51.4.1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Motion",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,Penny) & Component-of(c,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1128": [
        "He skated Penny around the rink",
        "vehicle-51.4.1",
        "Sbj V Obj PathP",
        "NP V NP PP.location",
        "Volitional Motion",
        "DirectedActivity",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,Penny) & Component-of(c,rink) & UndAct(a,i,j,q1) & DirAct(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1129": [
        "He waltzed her across the floor",
        "waltz-51.5",
        "Sbj V Obj PathP",
        "NP V NP PP.trajectory",
        "Volitional Motion",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,her) & Component-of(c,floor) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & MOT(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1130": [
        "Clouds cleared from the sky.",
        "clear-10.3-1",
        "Sbj V PathP",
        "NP V PP.location",
        "Autonomous Remove",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,Clouds) & Component-of(b,sky) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & -MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1131": [
        "The cream separated easily from (the) milk",
        "separate-23.1",
        "Sbj V PathP",
        "NP V ADVP-Middle PP",
        "Autonomous Remove",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,cream) & Component-of(b,milk) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & -MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1132": [
        "The yolk separated from the white",
        "separate-23.1-1",
        "Sbj V PathP",
        "NP V PP.co-patient",
        "Autonomous Remove",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,yolk) & Component-of(b,white) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & -MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1133": [
        "The twig broke off the branch",
        "split-23.2",
        "Sbj V PathP",
        "NP V PP.co-patient",
        "Autonomous Remove",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,twig) & Component-of(b,branch) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & -MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1134": [
        "The twigs broke off of those branches easily",
        "split-23.2",
        "Sbj V PathP",
        "NP V PP ADV-Middle",
        "Autonomous Remove",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,twigs) & Component-of(b,branches) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & -MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "1135": [
        "Susan cut the recipes from the magazine with a sharp knife",
        "cut-21.1",
        "Sbj V Obj PathP with Obl",
        "NP V NP PP.source PP.instrument",
        "Instrument Remove",
        "IncrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,Susan) & Component-of(b,knife) & Component-of(c,recipes) & Component-of(d,magazine) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & InhStPh(d,i,m,q4) & VOL(q1) & -MER(q3) & FRC(a,b) & FRC(b,c) & PTH(c,d)"
    ],
    "1136": [
        "Doug cleaned the dishes from the table",
        "clear-10.3",
        "Sbj V Obj PathP",
        "NP V NP PP.location",
        "Volitional Remove",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Doug) & Component-of(b,dishes) & Component-of(c,table) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1137": [
        "Sympathetic fans clipped copies of Ms. Shere's recipes from magazines",
        "cut-21.1",
        "Sbj V Obj PathP",
        "NP V NP PP.source",
        "Volitional Remove",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,fans) & Component-of(b,copies of Ms. Shere's recipes) & Component-of(c,magazines) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1138": [
        "I unscrewed the handle",
        "disassemble-23.3",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Remove",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,handle) & Component-of(c,NI) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1139": [
        "I unscrewed the handle from the box",
        "disassemble-23.3",
        "Sbj V Obj PathP",
        "NP V NP PP.co-patient",
        "Volitional Remove",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,handle) & Component-of(c,box) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1140": [
        "The men mined the gold",
        "mine-10.9",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Remove",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,men) & Component-of(b,gold) & Component-of(c,NI) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1141": [
        "The men mined the gold from the abandoned mine",
        "mine-10.9",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location",
        "Volitional Remove",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,men) & Component-of(b,gold) & Component-of(c,mine) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1142": [
        "Doug removed the smudges",
        "remove-10.1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Remove",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Doug) & Component-of(b,smudges) & Component-of(c,NI) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1143": [
        "Doug removed the smudges from the tabletop",
        "remove-10.1",
        "Sbj V Obj PathP",
        "NP V NP PP.source",
        "Volitional Remove",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Doug) & Component-of(b,smudges) & Component-of(c,tabletop) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1144": [
        "I separated the yolk from the white",
        "separate-23.1",
        "Sbj V Obj PathP",
        "NP V NP PP.co-patient",
        "Volitional Remove",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,yolk) & Component-of(c,white) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1145": [
        "I broke the twig off the branch",
        "split-23.2",
        "Sbj V Obj PathP",
        "NP V NP PP.co-patient",
        "Volitional Remove",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,twig) & Component-of(c,branch) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1146": [
        "Carla shoveled the snow from the walk",
        "wipe_instr-10.4.2",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location",
        "Volitional Remove",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Carla) & Component-of(b,snow) & Component-of(c,walk) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1147": [
        "Barry Cryer erased the writing",
        "wipe_manner-10.4.1",
        "Sbj V Obj",
        "NP V NP.theme",
        "Volitional Remove",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Barry Cryer) & Component-of(b,writing) & Component-of(c,NI) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1148": [
        "Brian wiped the fingerprints from the counter",
        "wipe_manner-10.4.1",
        "Sbj V Obj PathP",
        "NP V NP PP.source",
        "Volitional Remove",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Brian) & Component-of(b,fingerprints) & Component-of(c,counter) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & -MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1149": [
        "Sandy sang a song for me",
        "performance-26.7-1",
        "Sbj V Obj for Obl",
        "NP V NP PP.beneficiary",
        "Volitional Replicate Affect",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Sandy) & Component-of(b,song) & Component-of(c,me) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & DES(q2) & FRC(a,b) & AFF(b,c)"
    ],
    "1151": [
        "Sandy sang",
        "performance-26.7-1",
        "Sbj V",
        "NP V",
        "Volitional Replicate",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Sandy) & Component-of(b,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "1152": [
        "He rehearsed",
        "rehearse-26.8-1",
        "Sbj V",
        "NP V",
        "Volitional Replicate",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "1153": [
        "Sandy sang a song",
        "performance-26.7-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Replicate",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Sandy) & Component-of(b,song) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "1154": [
        "He rehearsed the song",
        "rehearse-26.8",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Replicate",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,song) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "1155": [
        "He rehearsed singing the song",
        "rehearse-26.8",
        "Sbj V Obj",
        "NP V S_ING",
        "Volitional Replicate",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,song) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "1156": [
        "The secretary transcribed the speech",
        "transcribe-25.4",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Replicate",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,secretary) & Component-of(b,speech) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "1157": [
        "The sky cleared",
        "clear-10.3-1",
        "Sbj V",
        "NP.location V",
        "Autonomous Uncover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,NI) & Component-of(b,sky) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & -MER(q2) & EXIST(q2) & PTH(a,b)"
    ],
    "1158": [
        "Carla was vacuuming",
        "wipe_instr-10.4.2",
        "Sbj V",
        "NP V",
        "Volitional Uncover",
        "UndirectedActivity",
        "Theme-of(z,e) & Component-of(a,Carla) & Component-of(b,NI) & Component-of(c,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & UndAct(c,i,l,q3) & VOL(q1) & -MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1160": [
        "The cook deboned the fish",
        "debone-10.8",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Uncover",
        "IncrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,cook) & Component-of(b,NI) & Component-of(c,fish) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & -MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1161": [
        "The cook boned the fish",
        "pit-10.7",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Uncover",
        "IncrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,cook) & Component-of(b,NI) & Component-of(c,fish) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & -MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1162": [
        "I bled him",
        "substance_emission-43.4-1-1",
        "Sbj V Obj",
        "NP V NP.source",
        "Volitional Uncover",
        "IncrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,I) & Component-of(b,NI) & Component-of(c,him) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & -MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1163": [
        "Carla shoveled the walk",
        "wipe_instr-10.4.2",
        "Sbj V Obj",
        "NP V NP.initial_location",
        "Volitional Uncover",
        "IncrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,Carla) & Component-of(b,NI) & Component-of(c,walk) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & -MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1164": [
        "Carla shoveled the walk clean",
        "wipe_instr-10.4.2",
        "Sbj V Obj ResultP",
        "NP V NP ADJP-Result",
        "Volitional Uncover",
        "IncrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,Carla) & Component-of(b,NI) & Component-of(c,walk) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & -MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1165": [
        "Brian wiped the counter",
        "wipe_manner-10.4.1",
        "Sbj V Obj",
        "NP V NP.source",
        "Volitional Uncover",
        "IncrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,Brian) & Component-of(b,NI) & Component-of(c,counter) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & -MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1167": [
        "Doug cleaned the table of dishes",
        "clear-10.3",
        "Sbj V Obj of Obl",
        "NP V NP.location PP.theme",
        "Volitional Uncover",
        "IncrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,Doug) & Component-of(b,dishes) & Component-of(c,table) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & -MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "1168": [
        "Jill took a cab",
        "vehicle_path-51.4.3",
        "Sbj V Obj",
        "NP V NP",
        "Facilitating ",
        "TransitoryState",
        "N/A & Component-of(a,Jill) & Component-of(b,cab) & N/A & VOL(q1) & FAC(a,b)"
    ],
    "664": [
        "The grocery cart hit against the wall",
        "bump-18.4",
        "Sbj V PathP",
        "NP V PP.location",
        "Autonomous Apply",
        "CyclicAchievement",
        "Theme-of(x,e) & Component-of(a,cart) & Component-of(b,wall) & CycAch(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "665": [
        "That type of rope coiled easily around the post",
        "coil-9.6",
        "Sbj V PathP",
        "NP V ADV-Middle PP.location",
        "Autonomous Apply",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,type type of rope) & Component-of(b,post) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "666": [
        "The rope coiled around the post",
        "coil-9.6",
        "Sbj V PathP",
        "NP V PP.location",
        "Autonomous Apply",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,rope) & Component-of(b,post) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "667": [
        "The company is wedging into new markets",
        "funnel-9.3-1-1",
        "Sbj V PathP",
        "NP V PP.destination",
        "Autonomous Apply",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,company) & Component-of(b,markets) & DirAct(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "668": [
        "The eggs mixed well with (the) cream",
        "mix-22.1-1",
        "Sbj V PathP",
        "NP V ADVP-Middle PP",
        "Autonomous Apply",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,eggs) & Component-of(b,cream) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "669": [
        "The computer connected well to the network",
        "mix-22.1-2",
        "Sbj V PathP",
        "NP V ADVP-Middle PP",
        "Autonomous Apply",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,computer) & Component-of(b,network) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "670": [
        "My computer connected to his computer",
        "mix-22.1-2-1",
        "Sbj V PathP",
        "NP V PP.patient",
        "Autonomous Apply",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,computer) & Component-of(b,computer) & DirAch(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "671": [
        "Water poured from the bowl into the cup",
        "pour-9.5",
        "Sbj V PathP",
        "NP V PP.initial_location PP.destination",
        "Autonomous Apply",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,Water) & Component-of(b,cup) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "672": [
        "Water poured onto the plants",
        "pour-9.5",
        "Sbj V PathP",
        "NP V PP.destination",
        "Autonomous Apply",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,Water) & Component-of(b,plants) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "673": [
        "The books lean against the shelf",
        "put_spatial-9.2-1",
        "Sbj V PathP",
        "NP V PP.destination",
        "Autonomous Apply",
        "TransitoryState",
        "Theme-of(x,e) & Component-of(a,books) & Component-of(b,shelf) & TranStPh(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "674": [
        "The books lean there",
        "put_spatial-9.2-1",
        "Sbj V PathP",
        "NP V ADVP",
        "Autonomous Apply",
        "TransitoryState",
        "Theme-of(x,e) & Component-of(a,books) & Component-of(b,there) & TranStPh(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "675": [
        "The sugar whipped into (the) cream easily",
        "shake-22.3-1-1",
        "Sbj V PathP",
        "NP V PP ADV-Middle",
        "Autonomous Apply",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,sugar) & Component-of(b,cream) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "676": [
        "Paint sprayed onto the wall",
        "spray-9.7-1",
        "Sbj V PathP",
        "NP V PP.destination",
        "Autonomous Apply",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,Paint) & Component-of(b,wall) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "677": [
        "The labels taped easily to that kind of cover",
        "tape-22.4",
        "Sbj V PathP",
        "NP V ADV-Middle PP",
        "Autonomous Apply",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,labels) & Component-of(b,cover) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "678": [
        "It clamped on his ankle",
        "tape-22.4-1",
        "Sbj V PathP",
        "NP V PP.co-patient",
        "Autonomous Apply",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,It) & Component-of(b,ankle) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "679": [
        "The child clung to her mother",
        "cling-22.5",
        "Sbj V PathP",
        "NP V PP.co-theme",
        "Self-volitional Apply",
        "TransitoryState",
        "Theme-of(x,e) & Component-of(a,child) & Component-of(b,mother) & TranStPh(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "680": [
        "She was always clad in black",
        "being_dressed-41.3.3",
        "Sbj V Obj PathP",
        "Passive",
        "Self-volitional Apply",
        "",
        "Theme-of(x,e) & Component-of(a,She) & Component-of(b,black) & TranStPh(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & +MER(q1) & EXIST(q2) & PTH(a,b)"
    ],
    "681": [
        "Diabetics can now incorporate sugar into their desserts",
        "amalgamate-22.2-1",
        "Sbj V Obj PathP",
        "NP V NP PP.co-patient",
        "Volitional Apply",
        "",
        "N/A & Component-of(a,Diabetics) & Component-of(b,sugar) & Component-of(c,desserts) & N/A & VOL(q1) & +MER(q2) & FRC(a,b) & PTH(b,c)"
    ],
    "682": [
        "Cora coiled the rope around the post",
        "coil-9.6",
        "Sbj V Obj PathP",
        "NP V NP PP.location",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Cora) & Component-of(b,rope) & Component-of(c,post) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "683": [
        "I spooned the sauce there",
        "funnel-9.3",
        "Sbj V Obj PathP",
        "NP V NP ADVP",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,sauce) & Component-of(c,there) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "684": [
        "I funneled the mixture into the bottle",
        "funnel-9.3",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,mixture) & Component-of(c,bottle) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "685": [
        "He wedged the diamond between shifting dunes",
        "funnel-9.3-1",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,diamond) & Component-of(c,dunes) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "686": [
        "Paula hit the stick against/on the fence",
        "hit-18.1",
        "Sbj V Obj PathP",
        "NP V NP PP",
        "Volitional Apply",
        "CyclicAchievement",
        "Theme-of(y,e) & Component-of(a,Paula) & Component-of(b,stick) & Component-of(c,fence) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "687": [
        "Smith inscribed his name on the ring",
        "image_impression-25.1",
        "Sbj V Obj PathP",
        "NP V NP.theme PP.destination",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Smith) & Component-of(b,name) & Component-of(c,ring) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "688": [
        "Herman added a computer to the network",
        "mix-22.1-2",
        "Sbj V Obj PathP",
        "NP V NP PP.co-patient",
        "Volitional Apply",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,computer) & Component-of(c,network) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "689": [
        "Lydia pocketed the change in her left pocket",
        "pocket-9.10",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Apply",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Lydia) & Component-of(b,change) & Component-of(c,pocket) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "690": [
        "Allison poked the needle through the cloth",
        "poke-19",
        "Sbj V Obj PathP",
        "NP V NP PP.patient",
        "Volitional Apply",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Allison) & Component-of(b,needle) & Component-of(c,cloth) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "691": [
        "Maria poured water from the bowl into the cup",
        "pour-9.5",
        "Sbj V Obj PathP",
        "NP V NP PP.initial_location PP.destination",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Maria) & Component-of(b,water) & Component-of(c,cup) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "692": [
        "Tamara poured water here",
        "pour-9.5",
        "Sbj V Obj PathP",
        "NP V NP ADVP",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Tamara) & Component-of(b,water) & Component-of(c,here) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "693": [
        "Tamara poured water into the bowl",
        "pour-9.5",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Tamara) & Component-of(b,water) & Component-of(c,bowl) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "694": [
        "I dropped the books here",
        "put_direction-9.4",
        "Sbj V Obj PathP",
        "NP V NP ADVP",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,books) & Component-of(c,here) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "695": [
        "I lifted the books onto the table",
        "put_direction-9.4",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,books) & Component-of(c,table) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "696": [
        "Cheryl stood the books on the shelf",
        "put_spatial-9.2",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Cheryl) & Component-of(b,books) & Component-of(c,shelf) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "697": [
        "Cheryl stood the books there",
        "put_spatial-9.2",
        "Sbj V Obj PathP",
        "NP V NP ADVP",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Cheryl) & Component-of(b,books) & Component-of(c,there) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "698": [
        "I put the book on/under/near the table",
        "put-9.1",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Apply",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,book) & Component-of(c,table) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "699": [
        "I put the book here/there",
        "put-9.1",
        "Sbj V Obj PathP",
        "NP V NP ADVP",
        "Volitional Apply",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,book) & Component-of(c,here) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "700": [
        "They put upon me a brilliant, red helm",
        "put-9.1-2",
        "Sbj V Obj PathP",
        "NP V PP.destination NP",
        "Volitional Apply",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,They) & Component-of(b,helm) & Component-of(c,me) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "701": [
        "Saul jotted down readings on a notepad",
        "scribble-25.2",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Apply",
        "DirectedActivity",
        "Theme-of(y,e) & Component-of(a,Saul) & Component-of(b,readings) & Component-of(c,notepad) & UndAct(a,i,j,q1) & DirAct(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "702": [
        "They stood the statue on the pedestal",
        "spatial_configuration-47.6",
        "Sbj V Obj PathP",
        "NP V NP.theme PP",
        "Volitional Apply",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,They) & Component-of(b,statue) & Component-of(c,pedestal) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "703": [
        "Jessica loaded boxes into the wagon",
        "spray-9.7",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Jessica) & Component-of(b,boxes) & Component-of(c,wagon) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "704": [
        "Linda taped the picture to the wall",
        "tape-22.4",
        "Sbj V Obj PathP",
        "NP V NP PP.co-patient",
        "Volitional Apply",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Linda) & Component-of(b,picture) & Component-of(c,wall) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "705": [
        "The secretary transcribed the speech into the record",
        "transcribe-25.4",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,secretary) & Component-of(b,speech) & Component-of(c,record) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "706": [
        "He plowed the snow back into the ditch",
        "wipe_instr-10.4.2-1",
        "Sbj V Obj PathP",
        "NP V NP PP.destination",
        "Volitional Apply",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,snow) & Component-of(c,ditch) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "707": [
        "Lydia pocketed the change",
        "pocket-9.10",
        "Sbj V Obj",
        "NP V NP.theme",
        "Volitional Apply",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Lydia) & Component-of(b,change) & Component-of(c,NI) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "708": [
        "I stashed the book",
        "put-9.1-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Apply",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,book) & Component-of(c,NI) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & InhStPh(c,i,l,q3) & VOL(q1) & +MER(q2) & EXIST(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "709": [
        "She always wears purple dresses",
        "simple_dressing-41.3.1",
        "Sbj V Obj",
        "NP V NP",
        "Self-volitional Constrain",
        "",
        "N/A & Component-of(a,She) & Component-of(b,dresses) & N/A & VOL(q1) & CTR(a,b)"
    ],
    "710": [
        "The rod bent",
        "bend-45.2",
        "Sbj V",
        "NP.patient V",
        "Autonomous COS",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,rod) & DirAch(a,i,j,q1) & COS(q1)"
    ],
    "711": [
        "The copper rods bent easily",
        "bend-45.2",
        "Sbj V",
        "NP V ADV-Middle",
        "Autonomous COS",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,rods) & IncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "712": [
        "The bridge gave way",
        "break_down-45.8",
        "Sbj V",
        "NP V",
        "Autonomous COS",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,bridge) & DirAch(a,i,j,q1) & COS(q1)"
    ],
    "713": [
        "The window broke",
        "break-45.1",
        "Sbj V",
        "NP.patient V",
        "Autonomous COS",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,window) & DirAch(a,i,j,q1) & COS(q1)"
    ],
    "714": [
        "The glass broke into a thousand pieces",
        "break-45.1",
        "Sbj V ResultP",
        "NP V PP.result",
        "Autonomous COS",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,glass) & DirAch(a,i,j,q1) & COS(q1)"
    ],
    "715": [
        "The crystal vases broke easily",
        "break-45.1",
        "Sbj V",
        "NP V ADV-Middle",
        "Autonomous COS",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,vases) & IncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "716": [
        "This wood carved beautiful toys",
        "build-26.1",
        "Sbj V ResultP",
        "NP.material V NP",
        "Autonomous COS",
        "NonincrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,wood) & NonIncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "718": [
        "He died",
        "die-42.4",
        "Sbj V",
        "NP V",
        "Autonomous COS",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,He) & DirAch(a,i,j,q1) & COS(q1)"
    ],
    "719": [
        "The roses bloomed",
        "entity_specific_cos-45.5",
        "Sbj V",
        "NP.patient V",
        "Autonomous COS",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,roses) & IncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "720": [
        "That acorn will grow into an oak tree",
        "grow-26.2.1",
        "Sbj V ResultP",
        "NP.material V PP.product",
        "Autonomous COS",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,acorn) & IncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "721": [
        "The dough twirled into a pretzel",
        "knead-26.5",
        "Sbj V ResultP",
        "NP.material V PP.product",
        "Autonomous COS",
        "NonincrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,dough) & NonIncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "722": [
        "The cotton clothes dried easily",
        "other_cos-45.4",
        "Sbj V",
        "NP V ADV-Middle",
        "Autonomous COS",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,clothes) & IncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "723": [
        "The clothes dried",
        "other_cos-45.4",
        "Sbj V",
        "NP.patient V",
        "Autonomous COS",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,clothes) & IncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "724": [
        "The clothes dried wrinkled",
        "other_cos-45.4-1",
        "Sbj V ResultP",
        "NP V NP ADJ",
        "Autonomous COS",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,clothes) & IncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "725": [
        "The new tractors repaired easily",
        "remedy-45.7-1",
        "Sbj V",
        "NP V ADV-Middle",
        "Autonomous COS",
        "NonincrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,tractors) & NonIncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "726": [
        "The drawer rolled to an open position",
        "roll-51.3.1",
        "Sbj V ResultP",
        "NP V PP.result",
        "Autonomous COS",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,drawer) & IncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "727": [
        "The drawer rolled open",
        "roll-51.3.1",
        "Sbj V ResultP",
        "NP V ADJ",
        "Autonomous COS",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,drawer) & IncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "728": [
        "The twig and the branch broke apart",
        "split-23.2",
        "Sbj V ResultP",
        "NP V apart",
        "Autonomous COS",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,twig and the branch) & DirAch(a,i,j,q1) & COS(q1)"
    ],
    "729": [
        "The sailor drowned",
        "suffocate-40.7",
        "Sbj V",
        "NP.theme V",
        "Autonomous COS",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,sailor) & DirAch(a,i,j,q1) & COS(q1)"
    ],
    "730": [
        "He choked/suffocated to death",
        "suffocate-40.7",
        "Sbj V ResultP",
        "NP V PP.result",
        "Autonomous COS",
        "NonincrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,He) & NonIncrAcc(a,i,j,q1) & COS(q1)"
    ],
    "731": [
        "He turned from a prince into a frog",
        "turn-26.6.1",
        "Sbj V ResultP",
        "NP.patient V PP.material PP.result",
        "Autonomous COS",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,He) & DirAch(a,i,j,q1) & COS(q1)"
    ],
    "732": [
        "He turned into a frog",
        "turn-26.6.1",
        "Sbj V ResultP",
        "NP.patient V PP.result",
        "Autonomous COS",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,He) & DirAch(a,i,j,q1) & COS(q1)"
    ],
    "733": [
        "Tony bent the rod into a U with pliers",
        "bend-45.2",
        "Sbj V Obj ResultP with Obl",
        "NP V NP PP.result PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,Tony) & Component-of(b,pliers) & Component-of(c,rod) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "734": [
        "Tony bent the rod with pliers",
        "bend-45.2",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,Tony) & Component-of(b,pliers) & Component-of(c,rod) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "735": [
        "Tony broke the glass to pieces with a hammer",
        "break-45.1",
        "Sbj V Obj ResultP with Obl",
        "NP V NP PP.result PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,Tony) & Component-of(b,hammer) & Component-of(c,glass) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "736": [
        "Tony broke the piggy bank open with a hammer",
        "break-45.1",
        "Sbj V Obj ResultP with Obl",
        "NP V NP ADJ PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,Tony) & Component-of(b,hammer) & Component-of(c,bank) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "737": [
        "Tony broke the window with a hammer",
        "break-45.1",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,Tony) & Component-of(b,hammer) & Component-of(c,window) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "738": [
        "Carol cut the envelope open with the knife",
        "cut-21.1",
        "Sbj V Obj ResultP with Obl",
        "NP V NP ADJP PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,Carol) & Component-of(b,knife) & Component-of(c,envelope) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "739": [
        "Carol cut the envelope into pieces with a knife",
        "cut-21.1",
        "Sbj V Obj ResultP with Obl",
        "NP V NP PP.result PP.instrument",
        "Instrument COS",
        "NonincrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,Carol) & Component-of(b,knife) & Component-of(c,envelope) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & NonIncrAcc(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "740": [
        "Carol cut the bread with a knife",
        "cut-21.1",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,Carol) & Component-of(b,knife) & Component-of(c,bread) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "741": [
        "The builders destroyed the warehouse with explosives",
        "destroy-44",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,builders) & Component-of(b,explosives) & Component-of(c,warehouse) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "742": [
        "She flossed her teeth with floss",
        "floss-41.2.1",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument COS",
        "IncrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,She) & Component-of(b,teeth) & Component-of(c,floss) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "743": [
        "Paul hit the window to pieces with a hammer",
        "hit-18.1",
        "Sbj V Obj ResultP with Obl",
        "NP V NP PP.result PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,Paul) & Component-of(b,hammer) & Component-of(c,window) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "744": [
        "Paul hit the door open with his foot",
        "hit-18.1",
        "Sbj V Obj ResultP with Obl",
        "NP V NP ADJP PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,Paul) & Component-of(b,foot) & Component-of(c,door) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "745": [
        "Caesar killed Brutus with a knife",
        "murder-42.1",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,Caesar) & Component-of(b,knife) & Component-of(c,Brutus) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "746": [
        "Bill dried the clothes with a hairdryer",
        "other_cos-45.4",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument COS",
        "IncrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,Bill) & Component-of(b,hairdryer) & Component-of(c,clothes) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "747": [
        "The queen poisoned Snow White with an apple",
        "poison-42.2",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,queen) & Component-of(b,apple) & Component-of(c,Snow White) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "748": [
        "Bill repaired the tractor with duct tape",
        "remedy-45.7",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument COS",
        "NonincrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,Bill) & Component-of(b,tape) & Component-of(c,tractor) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & NonIncrAcc(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "749": [
        "They spanked him to death with a bat",
        "spank-18.3",
        "Sbj V Obj ResultP with Obl",
        "NP V NP PP.result PP.instrument",
        "Instrument COS",
        "NonincrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,They) & Component-of(b,bat) & Component-of(c,him) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & NonIncrAcc(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "750": [
        "The cat clawed the couch to pieces with her sharp nails",
        "swat-18.2",
        "Sbj V Obj ResultP with Obl",
        "NP V NP PP.result PP.instrument",
        "Instrument COS",
        "NonincrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,cat) & Component-of(b,nails) & Component-of(c,couch) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & NonIncrAcc(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "751": [
        "Paula swatted the fly dead with a dishcloth",
        "swat-18.2",
        "Sbj V Obj ResultP with Obl",
        "NP V NP ADJP PP.instrument",
        "Instrument COS",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,Paula) & Component-of(b,dishcloth) & Component-of(c,fly) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "752": [
        "She brushed with a toothbrush",
        "floss-41.2.1",
        "Sbj V with Obl",
        "NP V PP.instrument",
        "Instrument COS",
        "UndirectedActivity",
        "Theme-of(z,e) & Component-of(a,She) & Component-of(b,toothbrush) & Component-of(c,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & UndAct(c,i,l,q3) & VOL(q1) & COS(q3) & FRC(a,b) & FRC(b,c)"
    ],
    "753": [
        "The pliers bent the rod",
        "bend-45.2",
        "Sbj V Obj",
        "NP.instrument V NP",
        "Physical COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,pliers) & Component-of(b,rod) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & COS(q2) & FRC(a,b)"
    ],
    "754": [
        "The hammer broke the window",
        "break-45.1",
        "Sbj V Obj",
        "NP.instrument V NP",
        "Physical COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,hammer) & Component-of(b,window) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & COS(q2) & FRC(a,b)"
    ],
    "755": [
        "The strong winds cleared the sky.",
        "clear-10.3",
        "Sbj V Obj",
        "NP V NP.location",
        "Physical COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,winds) & Component-of(b,sky) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & COS(q2) & FRC(a,b)"
    ],
    "756": [
        "The knife cut the envelope open",
        "cut-21.1",
        "Sbj V Obj ResultP",
        "NP V NP ADJP",
        "Physical COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,knife) & Component-of(b,envelope) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & COS(q2) & FRC(a,b)"
    ],
    "757": [
        "The knife cut the envelope into pieces",
        "cut-21.1",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Physical COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,knife) & Component-of(b,envelope) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & COS(q2) & FRC(a,b)"
    ],
    "758": [
        "The knife cut the bread",
        "cut-21.1",
        "Sbj V Obj",
        "NP.instrument V NP",
        "Physical COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,knife) & Component-of(b,bread) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & COS(q2) & FRC(a,b)"
    ],
    "759": [
        "The explosives destroyed the warehouse",
        "destroy-44",
        "Sbj V Obj",
        "NP.instrument V NP",
        "Physical COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,explosives) & Component-of(b,warehouse) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & COS(q2) & FRC(a,b)"
    ],
    "760": [
        "The stick hit the door open",
        "hit-18.1",
        "Sbj V Obj ResultP",
        "NP V NP ADJP",
        "Physical COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,stick) & Component-of(b,door) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & COS(q2) & FRC(a,b)"
    ],
    "761": [
        "The hammer hit the window to pieces",
        "hit-18.1",
        "Sbj V Obj ResultP",
        "NP V NP ADJP PP.result",
        "Physical COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,hammer) & Component-of(b,window) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & COS(q2) & FRC(a,b)"
    ],
    "762": [
        "The DDT killed the insects",
        "murder-42.1-1",
        "Sbj V Obj",
        "NP.instrument V NP",
        "Physical COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,DDT) & Component-of(b,insects) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & COS(q2) & FRC(a,b)"
    ],
    "763": [
        "The hairdryer dried the clothes",
        "other_cos-45.4",
        "Sbj V Obj",
        "NP.instrument V NP",
        "Physical COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,hairdryer) & Component-of(b,clothes) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & COS(q2) & FRC(a,b)"
    ],
    "764": [
        "Martha carved a piece of wood into a toy for the baby",
        "build-26.1",
        "Sbj V Obj ResultP for Obl",
        "NP V NP PP.product PP.beneficiary",
        "Volitional COS Affect",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Martha) & Component-of(b,piece of wood) & Component-of(c,baby) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & NonIncrAcc(c,i,l,q3) & VOL(q1) & COS(q2) & FRC(a,b) & AFF(b,c)"
    ],
    "765": [
        "Martha carved a piece of wood for the baby",
        "build-26.1",
        "Sbj V Obj for Obl",
        "NP V NP PP.beneficiary",
        "Volitional COS Affect",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Martha) & Component-of(b,piece of wood) & Component-of(c,baby) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & UndAct(c,i,l,q3) & VOL(q1) & COS(q2) & FRC(a,b) & AFF(b,c)"
    ],
    "766": [
        "The farmer cultivates the land for crops",
        "rear-26.2.2-1",
        "Sbj V Obj for Obl",
        "NP V NP.material PP.product",
        "Volitional COS Purp",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,farmer) & Component-of(b,land) & Component-of(c,crops) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & UndAct(c,i,l,q3) & VOL(q1) & COS(q2) & INT(q3) & FRC(a,b)"
    ],
    "767": [
        "Cynthia nibbled",
        "chew-39.2-1",
        "Sbj V",
        "NP V",
        "Volitional COS",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "768": [
        "Cynthia sipped",
        "chew-39.2-2",
        "Sbj V",
        "NP V",
        "Volitional COS",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "769": [
        "Cynthia ate",
        "eat-39.1-1",
        "Sbj V",
        "NP V",
        "Volitional COS",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "770": [
        "Cynthia drank",
        "eat-39.1-2",
        "Sbj V",
        "NP V",
        "Volitional COS",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "771": [
        "He's using",
        "eat-39.1-3",
        "Sbj V",
        "NP V",
        "Volitional COS",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "772": [
        "I flossed",
        "floss-41.2.1",
        "Sbj V",
        "NP V",
        "Volitional COS",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "773": [
        "Tony bent the rod",
        "bend-45.2",
        "Sbj V Obj",
        "NP V NP.patient",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Tony) & Component-of(b,rod) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "774": [
        "Tony bent the rod into a U",
        "bend-45.2",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Tony) & Component-of(b,rod) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "775": [
        "Tony folded the flaps open",
        "bend-45.2",
        "Sbj V Obj ResultP",
        "NP V NP ADJ",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Tony) & Component-of(b,flaps) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "776": [
        "Celia brushed the baby's hair",
        "braid-41.2.2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Celia) & Component-of(b,the baby's hair) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "777": [
        "Tony broke the window",
        "break-45.1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Tony) & Component-of(b,window) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "778": [
        "Tony broke the piggy bank open",
        "break-45.1",
        "Sbj V Obj ResultP",
        "NP V NP ADJ",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Tony) & Component-of(b,bank) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "779": [
        "Tony broke the glass to pieces",
        "break-45.1",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Tony) & Component-of(b,glass) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "780": [
        "Martha carved the piece of wood into a toy",
        "build-26.1",
        "Sbj V Obj ResultP",
        "NP V NP.material PP.product",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Martha) & Component-of(b,piece of wood) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "781": [
        "Cynthia nibbled the carrot",
        "chew-39.2-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "DirectedActivity",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,carrot) & UndAct(a,i,j,q1) & DirAct(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "782": [
        "Cynthia sipped the drink",
        "chew-39.2-2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "DirectedActivity",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,drink) & UndAct(a,i,j,q1) & DirAct(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "783": [
        "Claire painted the wall into a splotchy mess",
        "coloring-24",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Claire) & Component-of(b,wall) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "784": [
        "Claire painted the wall",
        "coloring-24",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "DirectedActivity",
        "Theme-of(y,e) & Component-of(a,Claire) & Component-of(b,wall) & UndAct(a,i,j,q1) & DirAct(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "785": [
        "Claire painted the wall red",
        "coloring-24",
        "Sbj V Obj ResultP",
        "NP V NP ADJP",
        "Volitional COS",
        "DirectedActivity",
        "Theme-of(y,e) & Component-of(a,Claire) & Component-of(b,wall) & UndAct(a,i,j,q1) & DirAct(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "786": [
        "Carol cut the envelop open",
        "cut-21.1",
        "Sbj V Obj ResultP",
        "NP V NP ADJP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Carol) & Component-of(b,envelop) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "787": [
        "Carol cut the envelope into pieces",
        "cut-21.1",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Carol) & Component-of(b,envelope) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "788": [
        "Carol cut through the bread",
        "cut-21.1",
        "Sbj V ResultP Obj",
        "NP V PP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Carol) & Component-of(b,y) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "789": [
        "Carol cut the bread",
        "cut-21.1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Carol) & Component-of(b,bread) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "790": [
        "Carol cut her finger",
        "cut-21.1-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Carol) & Component-of(b,finger) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "791": [
        "The Romans destroyed the city",
        "destroy-44",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Romans) & Component-of(b,city) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "792": [
        "Cynthia devoured the pizza",
        "devour-39.4",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,pizza) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "793": [
        "Cynthia ate the peach",
        "eat-39.1-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,peach) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "794": [
        "Cynthia drank the wine",
        "eat-39.1-2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,wine) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "795": [
        "She mainlines heroin",
        "eat-39.1-3",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "",
        "N/A & Component-of(a,She) & Component-of(b,heroin) & N/A & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "796": [
        "Paul inhaled water",
        "exhale-40.1.3-2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Paul) & Component-of(b,water) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "797": [
        "The hygienist flossed my teeth",
        "floss-41.2.1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,hygienist) & Component-of(b,teeth) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "798": [
        "Cynthia gobbled the pizza",
        "gobble-39.3-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,pizza) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "799": [
        "Cynthia gobbled the pizza down",
        "gobble-39.3-1",
        "Sbj V Obj ResultP",
        "NP V NP down",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,pizza) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "800": [
        "Cynthia gobbled the pizza up",
        "gobble-39.3-1",
        "Sbj V Obj ResultP",
        "NP V NP up",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,pizza) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "801": [
        "Cynthia quaffed her mead",
        "gobble-39.3-2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,mead) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "802": [
        "Cynthia quaffed down the mixture",
        "gobble-39.3-2",
        "Sbj V Obj ResultP",
        "NP V down NP",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Cynthia) & Component-of(b,mixture) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "803": [
        "Sheila groomed the horse",
        "groom-41.1.2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Sheila) & Component-of(b,horse) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "804": [
        "The gardener grew that acorn into an oak tree",
        "grow-26.2.1",
        "Sbj V Obj ResultP",
        "NP V NP.material PP.product",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,gardener) & Component-of(b,acorn) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "805": [
        "Paul kicked the door open",
        "hit-18.1",
        "Sbj V Obj ResultP",
        "NP V NP ADJP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Paul) & Component-of(b,door) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "806": [
        "Paul hit the window to pieces",
        "hit-18.1",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Paul) & Component-of(b,window) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "807": [
        "I kneaded the dough into a loaf",
        "knead-26.5",
        "Sbj V Obj ResultP",
        "NP V NP.material PP.product",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,dough) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "808": [
        "Brutus murdered Julius Caesar",
        "murder-42.1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Brutus) & Component-of(b,Caesar) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "809": [
        "Bill dried the clothes",
        "other_cos-45.4",
        "Sbj V Obj",
        "NP V NP.patient",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Bill) & Component-of(b,clothes) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "810": [
        "The witch poisoned Snow White",
        "poison-42.2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,witch) & Component-of(b,Snow White) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "811": [
        "The Boston Strangler strangled his victims to death",
        "poison-42.2",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Strangler) & Component-of(b,victims) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "812": [
        "The Boston Strangler strangled his victims dead",
        "poison-42.2",
        "Sbj V Obj ResultP",
        "NP V NP ADJ",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Boston Strangler) & Component-of(b,victims) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "813": [
        "Bill repaired the tractor",
        "remedy-45.7",
        "Sbj V Obj",
        "NP V NP.patient",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Bill) & Component-of(b,tractor) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "814": [
        "Bill rolled the drawer open",
        "roll-51.3.1",
        "Sbj V Obj ResultP",
        "NP V NP ADJ",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Bill) & Component-of(b,drawer) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "815": [
        "Bill rolled the drawer to an open position",
        "roll-51.3.1",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Bill) & Component-of(b,drawer) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "816": [
        "Tom walked the dog to exhaustion",
        "run-51.3.2-2",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Tom) & Component-of(b,dog) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "817": [
        "Herman whipped cream",
        "shake-22.3-1-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,cream) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "818": [
        "Herman gathered the students into a group",
        "shake-22.3-2",
        "Sbj V Obj ResultP",
        "NP V NP PP",
        "Volitional COS",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,students) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "819": [
        "They spanked him dead",
        "spank-18.3",
        "Sbj V Obj ResultP",
        "NP V NP ADJP",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,They) & Component-of(b,him) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "820": [
        "They spanked him to death",
        "spank-18.3",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,They) & Component-of(b,him) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "821": [
        "I broke the twig and the branch apart",
        "split-23.2",
        "Sbj V Obj ResultP",
        "NP V NP apart",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,twig and the branch) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "822": [
        "The pirates drowned the sailor",
        "suffocate-40.7",
        "Sbj V Obj",
        "NP V NP.theme",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,pirates) & Component-of(b,sailor) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "823": [
        "The pirate choked the sailor to death",
        "suffocate-40.7",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,pirate) & Component-of(b,sailor) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "824": [
        "Paula sliced the bag open",
        "swat-18.2",
        "Sbj V Obj ResultP",
        "NP V NP ADJP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Paula) & Component-of(b,bag) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "825": [
        "The cat clawed the couch to pieces",
        "swat-18.2",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,cat) & Component-of(b,couch) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "826": [
        "Linda taped the picture",
        "tape-22.4",
        "Sbj V Obj",
        "NP V NP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Linda) & Component-of(b,picture) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "827": [
        "Linda taped the box shut",
        "tape-22.4",
        "Sbj V Obj ResultP",
        "NP V NP ADJP",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Linda) & Component-of(b,box) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "828": [
        "The witch turned him from a prince into a frog",
        "turn-26.6.1",
        "Sbj V Obj ResultP",
        "NP V NP.patient PP.material PP.result",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,witch) & Component-of(b,him) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "829": [
        "The witch turned him into a frog",
        "turn-26.6.1",
        "Sbj V Obj ResultP",
        "NP V NP.patient PP.result",
        "Volitional COS",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,witch) & Component-of(b,him) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "830": [
        "He skated Penny to exhaustion",
        "vehicle-51.4.1",
        "Sbj V Obj ResultP",
        "NP V NP PP.result",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,Penny) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "831": [
        "He skated Penny exhausted",
        "vehicle-51.4.1",
        "Sbj V Obj ResultP",
        "NP V NP ADJ",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,Penny) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "832": [
        "He waltzed her to exhaustion",
        "waltz-51.5",
        "Sbj V Obj ResultP",
        "NP V NP PP.goal",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,her) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "833": [
        "He waltzed her dizzy",
        "waltz-51.5",
        "Sbj V Obj ResultP",
        "NP V NP ADJP",
        "Volitional COS",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,her) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & VOL(q1) & COS(q2) & FRC(a,b)"
    ],
    "834": [
        "The eggs mixed with the cream",
        "mix-22.1-1",
        "Sbj V with Obl",
        "NP V PP.co-patient",
        "Autonomous Cover",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,eggs) & Component-of(b,cream) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & +MER(q2) & EXIST(q2) & PTH(a,b)"
    ],
    "835": [
        "The employees staffed the store",
        "fill-9.8",
        "Sbj V Obj",
        "NP V NP",
        "Self-volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,employees) & Component-of(b,store) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & +MER(q2) & EXIST(q2) & PTH(a,b)"
    ],
    "836": [
        "Crowds packed the stands",
        "spray-9.7-1-1",
        "Sbj V Obj",
        "NP.theme V NP",
        "Self-volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,Crowds) & Component-of(b,stands) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & VOL(q1) & +MER(q2) & EXIST(q2) & PTH(a,b)"
    ],
    "837": [
        "Marlene dressed",
        "dress-41.1.1",
        "Sbj V",
        "NP V",
        "Self-volitional Cover",
        "UndirectedActivity",
        "N/A & Component-of(a,Marlene) & Component-of(b,NI) & Component-of(c,z) & N/A & VOL(q1) & +MER(q3) & PTH(b,c)"
    ],
    "838": [
        "Marlene dressed herself",
        "dress-41.1.1",
        "Sbj V Refl",
        "NP V NP",
        "Self-volitional Cover",
        "IncrementalAccomplishment",
        "N/A & Component-of(a,Marlene) & Component-of(b,NI) & Component-of(c,herself) & N/A & VOL(q1) & +MER(q3) & PTH(b,c)"
    ],
    "839": [
        "Lora buttered the toast",
        "butter-9.9",
        "Sbj V Obj",
        "NP V NP.destination",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Lora) & Component-of(b,NI) & Component-of(c,toast) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "840": [
        "Marlene dressed the baby",
        "dress-41.1.1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Marlene) & Component-of(b,NI) & Component-of(c,baby) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "841": [
        "Leslie covered the bed.",
        "fill-9.8",
        "Sbj V Obj",
        "NP V NP.destination",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Leslie) & Component-of(b,NI) & Component-of(c,bed) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "842": [
        "The jeweler decorated the ring",
        "illustrate-25.3",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,jeweler) & Component-of(b,NI) & Component-of(c,ring) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "843": [
        "Smith was inscribing the rings",
        "image_impression-25.1",
        "Sbj V Obj",
        "NP V NP.destination",
        "Volitional Cover",
        "DirectedActivity",
        "N/A & Component-of(a,Smith) & Component-of(b,NI) & Component-of(c,rings) & N/A & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "844": [
        "Jessica sprayed the wall",
        "spray-9.7",
        "Sbj V Obj",
        "NP V NP.destination",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Jessica) & Component-of(b,NI) & Component-of(c,wall) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "845": [
        "Lora buttered the toast with unsalted butter",
        "butter-9.9",
        "Sbj V Obj in/with Obl",
        "NP V NP PP.theme",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Lora) & Component-of(b,butter) & Component-of(c,toast) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "846": [
        "Leslie covered the bed with blankets.",
        "fill-9.8",
        "Sbj V Obj in/with Obl",
        "NP V NP PP.theme",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Leslie) & Component-of(b,blankets) & Component-of(c,bed) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "847": [
        "Leigh swaddled the baby in blankets",
        "fill-9.8-1",
        "Sbj V Obj in/with Obl",
        "NP V NP PP.theme",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Leigh) & Component-of(b,blankets) & Component-of(c,baby) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "848": [
        "The jeweler decorated the ring with the name",
        "illustrate-25.3",
        "Sbj V Obj in/with Obl",
        "NP V NP PP.theme",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,jeweler) & Component-of(b,name) & Component-of(c,ring) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "849": [
        "Smith inscribed the ring with his name",
        "image_impression-25.1",
        "Sbj V Obj in/with Obl",
        "NP V NP.destination PP.theme",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Smith) & Component-of(b,name) & Component-of(c,ring) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "850": [
        "Herman mixed the eggs with the cream",
        "mix-22.1-1",
        "Sbj V Obj in/with Obl",
        "NP V NP PP.co-patient",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,cream) & Component-of(c,eggs) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "851": [
        "Herman whipped sugar with the cream",
        "shake-22.3-1",
        "Sbj V Obj in/with Obl",
        "NP V NP PP.co-patient",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,cream) & Component-of(c,sugar) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "852": [
        "Jessica loaded the wagon with boxes",
        "spray-9.7",
        "Sbj V Obj in/with Obl",
        "NP V NP.destination PP.theme",
        "Volitional Cover",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Jessica) & Component-of(b,boxes) & Component-of(c,wagon) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & +MER(q3) & FRC(a,b) & PTH(b,c)"
    ],
    "853": [
        "The fountain gushed",
        "substance_emission-43.4-1",
        "Sbj V",
        "NP V",
        "Autonomous Create",
        "UndirectedActivity",
        "N/A & Component-of(a,fountain) & N/A & DES(q1)"
    ],
    "854": [
        "That chisel carved the statue",
        "carve-21.2-2",
        "Sbj V Obj",
        "NP.instrument V NP",
        "Physical Create",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,chisel) & Component-of(b,statue) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & DES(q2) & FRC(a,b)"
    ],
    "855": [
        "The well gushed oil",
        "substance_emission-43.4",
        "Sbj V Obj",
        "NP V NP",
        "Physical Create",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,well) & Component-of(b,oil) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & DES(q2) & FRC(a,b)"
    ],
    "856": [
        "Martha carved a toy for the baby",
        "build-26.1",
        "Sbj V Obj for Obl",
        "NP V NP PP.beneficiary",
        "Volitional Create Affect",
        "NonincrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Martha) & Component-of(b,toy) & Component-of(c,baby) & UndAct(a,i,j,q1) & NonIncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & DES(q2) & FRC(a,b) & AFF(b,c)"
    ],
    "857": [
        "David dug a hole for me",
        "create-26.4",
        "Sbj V Obj for Obl",
        "NP V NP PP.beneficiary",
        "Volitional Create Affect",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,David) & Component-of(b,hole) & Component-of(c,me) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & DES(q2) & FRC(a,b) & AFF(b,c)"
    ],
    "858": [
        "David dug me a hole",
        "create-26.4-1",
        "Sbj V Obj Obj",
        "NP V NP.beneficiary NP",
        "Volitional Create Affect",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,David) & Component-of(b,hole) & Component-of(c,me) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & DES(q2) & FRC(a,b) & AFF(b,c)"
    ],
    "860": [
        "Claire drew me a picture",
        "performance-26.7-1",
        "Sbj V Obj Obj",
        "NP V NP.beneficiary NP",
        "Volitional Create Affect",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Claire) & Component-of(b,picture) & Component-of(c,me) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & DES(q2) & FRC(a,b) & AFF(b,c)"
    ],
    "861": [
        "Donna fixed a sandwich for me",
        "preparing-26.3-1",
        "Sbj V Obj for Obl",
        "NP V NP PP.beneficiary",
        "Volitional Create Affect",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Donna) & Component-of(b,sandwich) & Component-of(c,me) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & DES(q2) & FRC(a,b) & AFF(b,c)"
    ],
    "862": [
        "Donna fixed me a sandwich",
        "preparing-26.3-1",
        "Sbj V Obj Obj",
        "NP V NP.beneficiary NP",
        "Volitional Create Affect",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Donna) & Component-of(b,sandwich) & Component-of(c,me) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & DES(q2) & FRC(a,b) & AFF(b,c)"
    ],
    "863": [
        "Donna grilled steaks for me",
        "preparing-26.3-2",
        "Sbj V Obj for Obl",
        "NP V NP PP.beneficiary",
        "Volitional Create Affect",
        "DirectedActivity",
        "Theme-of(y,e) & Component-of(a,Donna) & Component-of(b,steaks) & Component-of(c,me) & UndAct(a,i,j,q1) & DirAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & DES(q2) & FRC(a,b) & AFF(b,c)"
    ],
    "864": [
        "Donna grilled me steaks",
        "preparing-26.3-2",
        "Sbj V Obj Obj",
        "NP V NP.beneficiary NP",
        "Volitional Create Affect",
        "DirectedActivity",
        "Theme-of(y,e) & Component-of(a,Donna) & Component-of(b,steaks) & Component-of(c,me) & UndAct(a,i,j,q1) & DirAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & DES(q2) & FRC(a,b) & AFF(b,c)"
    ],
    "865": [
        "Martha carves",
        "build-26.1",
        "Sbj V",
        "NP V",
        "Volitional Create",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Martha) & Component-of(b,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "866": [
        "Smith was inscribing",
        "image_impression-25.1",
        "Sbj V",
        "NP V",
        "Volitional Create",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Smith) & Component-of(b,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "867": [
        "Claire drew",
        "create-26.4-1",
        "Sbj V",
        "NP V",
        "Volitional Create",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Claire) & Component-of(b,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "868": [
        "Smith was scribbling",
        "scribble-25.2-1",
        "Sbj V",
        "NP V",
        "Volitional Create",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Smith) & Component-of(b,NI) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "869": [
        "My wife had twins",
        "birth-28.2-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Create",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,wife) & Component-of(b,twins) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "870": [
        "The dragon breathed fire",
        "breathe-40.1.2",
        "Sbj V Obj",
        "NP V NP.theme",
        "Volitional Create",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,dragon) & Component-of(b,fire) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "871": [
        "Martha carves toys",
        "build-26.1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Create",
        "",
        "N/A & Component-of(a,Martha) & Component-of(b,toys) & N/A & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "872": [
        "David constructed a house",
        "create-26.4",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Create",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,David) & Component-of(b,house) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "873": [
        "Paul exhaled a breath",
        "exhale-40.1.3-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Create",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Paul) & Component-of(b,breath) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "874": [
        "Smith inscribed his name",
        "image_impression-25.1",
        "Sbj V Obj",
        "NP V NP.theme",
        "Volitional Create",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Smith) & Component-of(b,name) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "876": [
        "Donna fixed a sandwich",
        "preparing-26.3-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Create",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Donna) & Component-of(b,sandwich) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "877": [
        "Donna grilled steaks",
        "preparing-26.3-2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Create",
        "DirectedActivity",
        "Theme-of(y,e) & Component-of(a,Donna) & Component-of(b,steaks) & UndAct(a,i,j,q1) & DirAct(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "878": [
        "My neighbor raises fruit trees",
        "rear-26.2.2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Create",
        "",
        "N/A & Component-of(a,neighbor) & Component-of(b,trees) & N/A & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "879": [
        "Roberto took notes",
        "scribble-25.2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Create",
        "DirectedActivity",
        "Theme-of(y,e) & Component-of(a,Roberto) & Component-of(b,notes) & UndAct(a,i,j,q1) & DirAct(b,i,k,q2) & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "880": [
        "The stagehand flashed the lights",
        "light_emission-43.1",
        "Sbj V Obj",
        "NP V NP.theme",
        "Volitional Create",
        "CyclicAchievement",
        "N/A & Component-of(a,stagehand) & Component-of(b,lights) & N/A & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "881": [
        "I buzzed the bell",
        "sound_emission-43.2",
        "Sbj V Obj",
        "NP V NP.theme",
        "Volitional Create",
        "CyclicAchievement",
        "N/A & Component-of(a,I) & Component-of(b,bell) & N/A & VOL(q1) & DES(q2) & FRC(a,b)"
    ],
    "882": [
        "The bag is bulging with groceries",
        "bulge-47.5.3",
        "Sbj V with/of Obl",
        "NP V PP.theme",
        "Autonomous Dynamic Texture",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,bag) & Component-of(b,groceries) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & INT(q2) & PTH(a,b)"
    ],
    "883": [
        "The garden flowered with roses",
        "entity_specific_modes_being-47.2",
        "Sbj V with/of Obl",
        "NP.location V PP.theme",
        "Autonomous Dynamic Texture",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,garden) & Component-of(b,roses) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & INT(q2) & PTH(a,b)"
    ],
    "884": [
        "The crown sparkled with jewels",
        "light_emission-43.1",
        "Sbj V with/of Obl",
        "NP.location V PP.theme",
        "Autonomous Dynamic Texture",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,crown) & Component-of(b,jewels) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & INT(q2) & PTH(a,b)"
    ],
    "885": [
        "The room reeked of onions",
        "smell_emission-43.3",
        "Sbj V with/of Obl",
        "NP V PP.theme",
        "Autonomous Dynamic Texture",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,room) & Component-of(b,onions) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & INT(q2) & PTH(a,b)"
    ],
    "886": [
        "The street sang with horns",
        "sound_emission-43.2",
        "Sbj V with/of Obl",
        "NP.location V PP.theme",
        "Autonomous Dynamic Texture",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,street) & Component-of(b,horns) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & INT(q2) & PTH(a,b)"
    ],
    "887": [
        "The hall echoed with voices",
        "sound_existence-47.4",
        "Sbj V with/of Obl",
        "NP.location V NP.theme",
        "Autonomous Dynamic Texture",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,hall) & Component-of(b,voices) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & INT(q2) & PTH(a,b)"
    ],
    "888": [
        "The streets gushed with water",
        "substance_emission-43.4-1",
        "Sbj V with/of Obl",
        "NP.location V PP.theme",
        "Autonomous Dynamic Texture",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,streets) & Component-of(b,water) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & INT(q2) & PTH(a,b)"
    ],
    "889": [
        "The garden is swarming with bees",
        "swarm-47.5.1-1",
        "Sbj V with/of Obl",
        "PP.location V PP.theme",
        "Autonomous Dynamic Texture",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,garden) & Component-of(b,bees) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & INT(q2) & PTH(a,b)"
    ],
    "890": [
        "The garden abounds with flowers",
        "swarm-47.5.1-2-1",
        "Sbj V with/of Obl",
        "NP.location V PP.theme",
        "Autonomous Dynamic Texture",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,garden) & Component-of(b,flowers) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & INT(q2) & PTH(a,b)"
    ],
    "891": [
        "Paula spanked the naughty child on the back with a paddle",
        "spank-18.3",
        "Sbj V Obj LocP with Obl",
        "NP V NP PP PP.instrument",
        "Instrument Force XPR",
        "UndirectedActivity",
        "Theme-of(z,e) & Component-of(a,Paula) & Component-of(b,paddle) & Component-of(c,child) & Component-of(d,back) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & UndAct(c,i,l,q3) & UndAct(d,i,m,q4) & VOL(q1) & FRC(a,b) & FRC(b,c) & XPR(c,d)"
    ],
    "892": [
        "Carol crushed the ice with a hammer",
        "carve-21.2-1",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument Force",
        "DirectedAchievement",
        "Theme-of(z,e) & Component-of(a,Carol) & Component-of(b,hammer) & Component-of(c,ice) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & DirAch(c,i,l,q3) & VOL(q1) & FRC(a,b) & FRC(b,c)"
    ],
    "893": [
        "Carol carved the stone with a chisel",
        "carve-21.2-2",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument Force",
        "UndirectedActivity",
        "Theme-of(z,e) & Component-of(a,Carol) & Component-of(b,chisel) & Component-of(c,stone) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & UndAct(c,i,l,q3) & VOL(q1) & FRC(a,b) & FRC(b,c)"
    ],
    "894": [
        "Paula hit the ball with a stick",
        "hit-18.1",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument Force",
        "CyclicAchievement",
        "Theme-of(z,e) & Component-of(a,Paula) & Component-of(b,stick) & Component-of(c,ball) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & CycAch(c,i,l,q3) & VOL(q1) & FRC(a,b) & FRC(b,c)"
    ],
    "895": [
        "Steve pelted Anna with acorns",
        "pelt-17.2",
        "Sbj V Obj with Obl",
        "NP V NP PP.theme",
        "Instrument Force",
        "UndirectedActivity",
        "Theme-of(z,e) & Component-of(a,Steve) & Component-of(b,acorns) & Component-of(c,Anna) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & UndAct(c,i,l,q3) & VOL(q1) & FRC(a,b) & FRC(b,c)"
    ],
    "896": [
        "Allison poked the cloth with the needle",
        "poke-19",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument Force",
        "CyclicAchievement",
        "Theme-of(z,e) & Component-of(a,Allison) & Component-of(b,needle) & Component-of(c,cloth) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & CycAch(c,i,l,q3) & VOL(q1) & FRC(a,b) & FRC(b,c)"
    ],
    "897": [
        "Paula spanked the child with her right hand",
        "spank-18.3",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument Force",
        "UndirectedActivity",
        "Theme-of(z,e) & Component-of(a,Paula) & Component-of(b,hand) & Component-of(c,child) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & UndAct(c,i,l,q3) & VOL(q1) & FRC(a,b) & FRC(b,c)"
    ],
    "898": [
        "Paula swatted the fly with a dishcloth",
        "swat-18.2",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument Force",
        "CyclicAchievement",
        "Theme-of(z,e) & Component-of(a,Paula) & Component-of(b,dishcloth) & Component-of(c,fly) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & CycAch(c,i,l,q3) & VOL(q1) & FRC(a,b) & FRC(b,c)"
    ],
    "899": [
        "Carrie touched the cat with the stick",
        "touch-20",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument Force",
        "CyclicAchievement",
        "Theme-of(z,e) & Component-of(a,Carrie) & Component-of(b,stick) & Component-of(c,cat) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & CycAch(c,i,l,q3) & VOL(q1) & FRC(a,b) & FRC(b,c)"
    ],
    "900": [
        "Carrie touched his shoulder with the stick",
        "touch-20-1",
        "Sbj V Obj with Obl",
        "NP V NP PP.instrument",
        "Instrument Force",
        "CyclicAchievement",
        "Theme-of(z,e) & Component-of(a,Carrie) & Component-of(b,stick) & Component-of(c,shoulder) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & CycAch(c,i,l,q3) & VOL(q1) & FRC(a,b) & FRC(b,c)"
    ],
    "901": [
        "The hammer crushed the marble",
        "carve-21.2-1",
        "Sbj V Obj",
        "NP.instrument V NP",
        "Physical Force",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,hammer) & Component-of(b,marble) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & FRC(a,b)"
    ],
    "902": [
        "The stick hit the fence",
        "hit-18.1",
        "Sbj V Obj",
        "NP.instrument V NP",
        "Physical Force",
        "CyclicAchievement",
        "Theme-of(y,e) & Component-of(a,stick) & Component-of(b,fence) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & FRC(a,b)"
    ],
    "903": [
        "The needle poked the cloth",
        "poke-19",
        "Sbj V Obj",
        "NP.instrument V NP",
        "Physical Force",
        "CyclicAchievement",
        "Theme-of(y,e) & Component-of(a,needle) & Component-of(b,cloth) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & FRC(a,b)"
    ],
    "904": [
        "Paula spanked the naughty child on the back",
        "spank-18.3",
        "Sbj V Obj LocP",
        "NP V NP PP.location",
        "Volitional Force XPR",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Paula) & Component-of(b,child) & Component-of(c,back) & CycAch(a,i,j,q1) & UndAct(b,i,k,q2) & UndAct(c,i,l,q3) & VOL(q1) & FRC(a,b) & XPR(b,c)"
    ],
    "905": [
        "Paula swatted Deirdre on the back",
        "swat-18.2",
        "Sbj V Obj LocP",
        "NP V NP PP.location",
        "Volitional Force XPR",
        "CyclicAchievement",
        "Theme-of(y,e) & Component-of(a,Paula) & Component-of(b,Deirdre) & Component-of(c,back) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & CycAch(c,i,l,q3) & VOL(q1) & FRC(a,b) & XPR(b,c)"
    ],
    "906": [
        "Carol crushed the ice",
        "carve-21.2-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Force",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Carol) & Component-of(b,ice) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & CycAch(c,i,l,q3) & VOL(q1) & FRC(a,b)"
    ],
    "907": [
        "Carol carved the stone",
        "carve-21.2-2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Force",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Carol) & Component-of(b,stone) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & FRC(a,b)"
    ],
    "908": [
        "Paula hit the ball",
        "hit-18.1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Force",
        "CyclicAchievement",
        "Theme-of(y,e) & Component-of(a,Paula) & Component-of(b,ball) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & FRC(a,b)"
    ],
    "909": [
        "I kneaded the dough",
        "knead-26.5",
        "Sbj V Obj",
        "NP V NP.material",
        "Volitional Force",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,dough) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & FRC(a,b)"
    ],
    "910": [
        "He drove the car",
        "nonvehicle-51.4.2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Force",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,He) & Component-of(b,car) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & FRC(a,b)"
    ],
    "911": [
        "Steve pelted Anna",
        "pelt-17.2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Force",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Steve) & Component-of(b,Anna) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & FRC(a,b)"
    ],
    "912": [
        "Allison poked the cloth",
        "poke-19",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Force",
        "CyclicAchievement",
        "Theme-of(y,e) & Component-of(a,Allison) & Component-of(b,cloth) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & FRC(a,b)"
    ],
    "913": [
        "Paula spanked the child",
        "spank-18.3",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Force",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Paula) & Component-of(b,child) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & FRC(a,b)"
    ],
    "914": [
        "Paula spanked the naughty child's back",
        "spank-18.3",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Force",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,Paula) & Component-of(b,the naughty child's back) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & FRC(a,b)"
    ],
    "915": [
        "Paula swatted the fly",
        "swat-18.2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Force",
        "CyclicAchievement",
        "Theme-of(y,e) & Component-of(a,Paula) & Component-of(b,fly) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & FRC(a,b)"
    ],
    "916": [
        "Carrie touched the cat",
        "touch-20",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Force",
        "CyclicAchievement",
        "Theme-of(y,e) & Component-of(a,Carrie) & Component-of(b,cat) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & FRC(a,b)"
    ],
    "917": [
        "Carrie touched his shoulder",
        "touch-20-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Force",
        "CyclicAchievement",
        "Theme-of(y,e) & Component-of(a,Carrie) & Component-of(b,shoulder) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & FRC(a,b)"
    ],
    "918": [
        "An oak tree will grow from that acorn",
        "grow-26.2.1",
        "Sbj V from/out of Obl",
        "NP.product V PP.material",
        "Autonomous Form",
        "IncrementalAccomplishment",
        "???Theme-of(x,e) & Component-of(a,tree) & Component-of(b,acorn) & IncrAcc(a,i,j,q1) & InhStPh(b,i,k,q2) & DES(q2) & EXIST(q2) & FORM(a,b)"
    ],
    "919": [
        "Martha carved the baby a toy out of a piece of wood",
        "build-26.1",
        "Sbj V Obj from/out of Obl for Obl",
        "NP V NP.beneficiary NP PP",
        "Volitional Form Affect",
        "NonincrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,Martha) & Component-of(b,wood) & Component-of(c,toy) & Component-of(d,baby) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & NonIncrAcc(c,i,l,q3) & NonIncrAcc(d,i,m,q4) & VOL(q1) & DES(q3) & FRC(a,b) & FORM(b,c) & AFF(c,d)"
    ],
    "920": [
        "Martha carved a toy out of a piece of wood for the baby",
        "build-26.1",
        "Sbj V Obj from/out of Obl for Obl",
        "NP V NP PP.material PP.beneficiary",
        "Volitional Form Affect",
        "NonincrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,Martha) & Component-of(b,baby) & Component-of(c,wood) & Component-of(d,toy) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & NonIncrAcc(c,i,l,q3) & NonIncrAcc(d,i,m,q4) & VOL(q1) & DES(q3) & FRC(a,b) & FORM(b,c) & AFF(c,d)"
    ],
    "921": [
        "Martha carved a toy out of a piece of wood",
        "build-26.1",
        "Sbj V Obj from/out of Obl",
        "NP V NP.product PP.material",
        "Volitional Form",
        "NonincrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,Martha) & Component-of(b,wood) & Component-of(c,toy) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & NonIncrAcc(c,i,l,q3) & VOL(q1) & DES(q3) & FRC(a,b) & FORM(b,c)"
    ],
    "922": [
        "David constructed a house out of sticks",
        "create-26.4",
        "Sbj V Obj from/out of Obl",
        "NP V NP PP.material",
        "Volitional Form",
        "NonincrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,David) & Component-of(b,sticks) & Component-of(c,house) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & NonIncrAcc(c,i,l,q3) & VOL(q1) & DES(q3) & FRC(a,b) & FORM(b,c)"
    ],
    "923": [
        "The gardener grew an oak tree from that acorn",
        "grow-26.2.1",
        "Sbj V Obj from/out of Obl",
        "NP V NP.product PP.material",
        "Volitional Form",
        "IncrementalAccomplishment",
        "Theme-of(z,e) & Component-of(a,gardener) & Component-of(b,acorn) & Component-of(c,tree) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & IncrAcc(c,i,l,q3) & VOL(q1) & DES(q3) & FRC(a,b) & FORM(b,c)"
    ],
    "924": [
        "The jewel sparkled",
        "light_emission-43.1",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,jewel) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "925": [
        "The onions reeked",
        "smell_emission-43.3",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,onions) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "926": [
        "The room reeked",
        "smell_emission-43.3",
        "Sbj V",
        "NP.location V",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,room) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "927": [
        "The door hinges squeaked",
        "sound_emission-43.2",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,door hinges) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "928": [
        "The pieces interconnected easily",
        "amalgamate-22.2",
        "Sbj V",
        "NP V ADVP-Middle",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,pieces) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "929": [
        "The yolks and the whites intermingled",
        "amalgamate-22.2-1-1",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,yolks and the whites) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "930": [
        "The dog flopped",
        "assuming_position-50",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,dog) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "931": [
        "Sharon shivered",
        "body_internal_states-40.6",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Sharon) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "932": [
        "Paul breathed",
        "breathe-40.1.2",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Paul) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "933": [
        "Paul breathed a deep breath",
        "breathe-40.1.2-1",
        "Sbj V CogObj",
        "NP V NP",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,Paul) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "934": [
        "The bag is bulging",
        "bulge-47.5.3",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,bag) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "935": [
        "The grocery carts thudded together",
        "bump-18.4-1",
        "Sbj V",
        "NP V together",
        "Autonomous Internal",
        "CyclicAchievement",
        "Theme-of(x,e) & Component-of(a,carts) & CycAch(a,i,j,q1) & INT(q1)"
    ],
    "936": [
        "The cat kittened",
        "calve-28.1",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,cat) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "937": [
        "That hammer crushes well",
        "carve-21.2-1",
        "Sbj V",
        "NP.instrument V ADVP",
        "Autonomous Internal",
        "InherentState",
        "Theme-of(x,e) & Component-of(a,hammer) & InhStPh(a,i,j,q1) & INT(q1)"
    ],
    "938": [
        "The ice crushed easily",
        "carve-21.2-1",
        "Sbj V",
        "NP V ADVP-Middle",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,ice) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "939": [
        "That chisel carves well",
        "carve-21.2-2",
        "Sbj V",
        "NP.instrument V ADVP",
        "Autonomous Internal",
        "InherentState",
        "Theme-of(x,e) & Component-of(a,chisel) & InhStPh(a,i,j,q1) & INT(q1)"
    ],
    "940": [
        "The marble carved easily",
        "carve-21.2-2",
        "Sbj V",
        "NP V ADVP-Middle",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,marble) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "941": [
        "Italy and France touch",
        "contiguous_location-47.8-1",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "InherentState",
        "Theme-of(x,e) & Component-of(a,Italy and France) & InhStPh(a,i,j,q1) & INT(q1)"
    ],
    "942": [
        "This knife cuts well",
        "cut-21.1",
        "Sbj V",
        "NP.instrument V ADVP",
        "Autonomous Internal",
        "InherentState",
        "Theme-of(x,e) & Component-of(a,knife) & InhStPh(a,i,j,q1) & INT(q1)"
    ],
    "943": [
        "The bread cut easily",
        "cut-21.1",
        "Sbj V",
        "NP V ADVP-Middle",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,bread) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "944": [
        "That new handle unscrewed easily",
        "disassemble-23.3",
        "Sbj V",
        "NP V ADV-Middle",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,handle) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "945": [
        "The beer foamed",
        "entity_specific_modes_being-47.2",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,beer) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "946": [
        "There raged a fire",
        "entity_specific_modes_being-47.2",
        "Sbj V LocP",
        "There V NP",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,fire) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "947": [
        "Paul exhaled",
        "exhale-40.1.3-1",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,Paul) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "948": [
        "Paul inhaled",
        "exhale-40.1.3-2",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,Paul) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "949": [
        "Elvis lives",
        "exist-47.1",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "TransitoryState",
        "Theme-of(x,e) & Component-of(a,Elvis) & TranStPh(a,i,j,q1) & INT(q1)"
    ],
    "950": [
        "Sharon flinched",
        "flinch-40.5",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,Sharon) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "951": [
        "Paul hiccuped",
        "hiccup-40.1.1",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Paul) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "952": [
        "The river is twisting",
        "meander-47.7-1",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "InherentState",
        "Theme-of(x,e) & Component-of(a,river) & InhStPh(a,i,j,q1) & INT(q1)"
    ],
    "953": [
        "The eggs mixed well",
        "mix-22.1-1",
        "Sbj V",
        "NP V ADVP-Middle",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,eggs) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "954": [
        "The eggs and cream mixed well together",
        "mix-22.1-1",
        "Sbj V",
        "NP NP V ADVP-Middle together",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,eggs and cream) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "955": [
        "The eggs and the cream mixed together",
        "mix-22.1-1-1",
        "Sbj V",
        "NP NP V together",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,eggs and the cream) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "956": [
        "The eggs and the cream mixed",
        "mix-22.1-1-1",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,x) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "957": [
        "These computers connected well",
        "mix-22.1-2",
        "Sbj V",
        "NP V ADVP-Middle",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,computers) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "958": [
        "These computers connected well together",
        "mix-22.1-2",
        "Sbj V",
        "NP V ADVP-Middle",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,computers) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "959": [
        "Our computers connected",
        "mix-22.1-2-1",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,computers) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "960": [
        "Our computers connected together",
        "mix-22.1-2-1",
        "Sbj V",
        "NP V together",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,computers) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "961": [
        "A flag fluttered",
        "modes_of_being_with_motion-47.3",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,flag) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "962": [
        "There fluttered a flag (over the fort)",
        "modes_of_being_with_motion-47.3",
        "Sbj V LocP",
        "There V NP",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,flag) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "963": [
        "A serious accident happened",
        "occur-48.3",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,accident) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "964": [
        "There happened a serious accident",
        "occur-48.3",
        "Sbj V LocP",
        "There V NP",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,accident) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "965": [
        "The yolk and the white separated",
        "separate-23.1",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,yolk and the white) & DirAch(a,i,j,q1) & INT(q1)"
    ],
    "966": [
        "The egg yolks and egg whites separated easily",
        "separate-23.1",
        "Sbj V",
        "NP V ADVP-Middle",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,egg yolks and egg whites) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "967": [
        "The eggs whisked easily",
        "shake-22.3",
        "Sbj V",
        "NP V ADV-Middle",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,eggs) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "968": [
        "The sugar and cream whipped together easily",
        "shake-22.3",
        "Sbj V",
        "NP V together ADV-Middle",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,sugar and cream) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "969": [
        "Gloria snoozed",
        "snooze-40.4",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "TransitoryState",
        "Theme-of(x,e) & Component-of(a,Gloria) & TranStPh(a,i,j,q1) & INT(q1)"
    ],
    "970": [
        "Gloria slept the sleep of the dead",
        "snooze-40.4-1",
        "Sbj V CogObj",
        "NP V NP",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Gloria) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "971": [
        "The voices echoed",
        "sound_existence-47.4",
        "Sbj V",
        "NP V",
        "Autonomous Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,voices) & UndAct(a,i,j,q1) & INT(q1)"
    ],
    "972": [
        "Those twigs and branches broke apart easily",
        "split-23.2",
        "Sbj V",
        "NP V ADV-Middle",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,twigs and branches) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "973": [
        "The labels and covers taped together easily",
        "tape-22.4",
        "Sbj V",
        "NP V together ADV-Middle",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,labels and covers) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "974": [
        "The labels and covers taped easily together",
        "tape-22.4",
        "Sbj V",
        "NP V ADV-Middle together",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,labels and covers) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "975": [
        "The labels taped easily",
        "tape-22.4",
        "Sbj V",
        "NP V ADV-Middle",
        "Autonomous Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,labels) & IncrAcc(a,i,j,q1) & INT(q1)"
    ],
    "976": [
        "They multiplied",
        "birth-28.2",
        "Sbj V",
        "NP V",
        "Self-volitional Internal",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,They) & DirAct(a,i,j,q1) & VOL(q1) & INT(q1)"
    ],
    "977": [
        "Sylvia fidgeted",
        "body_internal_motion-49.1",
        "Sbj V",
        "NP V",
        "Self-volitional Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Sylvia) & UndAct(a,i,j,q1) & VOL(q1) & INT(q1)"
    ],
    "978": [
        "The child and her mother clung together",
        "cling-22.5",
        "Sbj V",
        "NP V together",
        "Self-volitional Internal",
        "TransitoryState",
        "Theme-of(x,e) & Component-of(a,child) & TranStPh(a,i,j,q1) & VOL(q1) & INT(q1)"
    ],
    "979": [
        "The princess curtseyed",
        "curtsey-40.3.3",
        "Sbj V",
        "NP V",
        "Self-volitional Internal",
        "CyclicAchievement",
        "Theme-of(x,e) & Component-of(a,princess) & CycAch(a,i,j,q1) & VOL(q1) & INT(q1)"
    ],
    "980": [
        "She spruced herself up before the job interview",
        "dressing_well-41.3.2",
        "Sbj V Refl",
        "NP V NP up",
        "Self-volitional Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,She) & IncrAcc(a,i,j,q1) & VOL(q1) & INT(q1)"
    ],
    "981": [
        "She spruced up herself before the job interview",
        "dressing_well-41.3.2",
        "Sbj V Refl",
        "NP V up NP",
        "Self-volitional Internal",
        "IncrementalAccomplishment",
        "Theme-of(x,e) & Component-of(a,She) & IncrAcc(a,i,j,q1) & VOL(q1) & INT(q1)"
    ],
    "982": [
        "The kids are assembling",
        "herd-47.5.2",
        "Sbj V",
        "NP V",
        "Self-volitional Internal",
        "DirectedActivity",
        "Theme-of(x,e) & Component-of(a,kids) & DirAct(a,i,j,q1) & VOL(q1) & INT(q1)"
    ],
    "983": [
        "Paul laughed",
        "nonverbal_expression-40.2",
        "Sbj V",
        "NP V",
        "Self-volitional Internal",
        "UndirectedActivity",
        "Theme-of(x,e) & Component-of(a,Paul) & UndAct(a,i,j,q1) & VOL(q1) & INT(q1)"
    ],
    "984": [
        "Paul laughed a cheerful laugh",
        "nonverbal_expression-40.2",
        "Sbj V CogObj",
        "NP V NP",
        "Self-volitional Internal",
        "CyclicAchievement",
        "Theme-of(x,e) & Component-of(a,Paul) & CycAch(a,i,j,q1) & VOL(q1) & INT(q1)"
    ],
    "985": [
        "John slouched",
        "spatial_configuration-47.6",
        "Sbj V",
        "NP V",
        "Self-volitional Internal",
        "DirectedAchievement",
        "Theme-of(x,e) & Component-of(a,John) & DirAch(a,i,j,q1) & VOL(q1) & INT(q1)"
    ],
    "986": [
        "Linda winked",
        "wink-40.3.1",
        "Sbj V",
        "NP V",
        "Self-volitional Internal",
        "CyclicAchievement",
        "Theme-of(x,e) & Component-of(a,Linda) & CycAch(a,i,j,q1) & VOL(q1) & INT(q1)"
    ],
    "987": [
        "Nora brought us together",
        "bring-11.3-1",
        "Sbj V Obj",
        "NP V NP together",
        "Volitional Internal",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Nora) & Component-of(b,us) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "988": [
        "Jennifer craned her neck",
        "crane-40.3.2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Internal",
        "CyclicAchievement",
        "Theme-of(y,e) & Component-of(a,Jennifer) & Component-of(b,neck) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "989": [
        "The teacher gathered the kids together",
        "herd-47.5.2",
        "Sbj V Obj",
        "NP V NP together",
        "Volitional Internal",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,teacher) & Component-of(b,kids) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "990": [
        "The teacher gathered the kids",
        "herd-47.5.2",
        "Sbj V Obj",
        "NP V NP.theme",
        "Volitional Internal",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,teacher) & Component-of(b,kids) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "991": [
        "Paula hit the sticks together",
        "hit-18.1",
        "Sbj V Obj",
        "NP V NP together",
        "Volitional Internal",
        "CyclicAchievement",
        "Theme-of(y,e) & Component-of(a,Paula) & Component-of(b,sticks) & CycAch(a,i,j,q1) & CycAch(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "992": [
        "Herman mixed the eggs",
        "mix-22.1-1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Internal",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,eggs) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "993": [
        "Herman mixed the eggs and the cream together",
        "mix-22.1-1",
        "Sbj V Obj",
        "NP V NP NP together",
        "Volitional Internal",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,eggs and the cream) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "994": [
        "Herman connected the computers",
        "mix-22.1-2",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Internal",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,computers) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "995": [
        "Herman connected the computers together",
        "mix-22.1-2",
        "Sbj V Obj",
        "NP V NP together",
        "Volitional Internal",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,computers) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "996": [
        "The patriots waved the flag",
        "modes_of_being_with_motion-47.3",
        "Sbj V Obj",
        "NP V NP.theme",
        "Volitional Internal",
        "UndirectedActivity",
        "Theme-of(y,e) & Component-of(a,patriots) & Component-of(b,flag) & UndAct(a,i,j,q1) & UndAct(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "997": [
        "I separated the yolk and the white",
        "separate-23.1",
        "Sbj V Obj",
        "NP V NP",
        "Volitional Internal",
        "DirectedAchievement",
        "Theme-of(y,e) & Component-of(a,I) & Component-of(b,yolk and the white) & CycAch(a,i,j,q1) & DirAch(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "998": [
        "Herman whipped sugar and the cream together",
        "shake-22.3-1",
        "Sbj V Obj",
        "NP V NP together",
        "Volitional Internal",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,sugar and the cream) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ],
    "999": [
        "Herman gathered the students together",
        "shake-22.3-2",
        "Sbj V Obj",
        "NP V NP together",
        "Volitional Internal",
        "IncrementalAccomplishment",
        "Theme-of(y,e) & Component-of(a,Herman) & Component-of(b,students) & UndAct(a,i,j,q1) & IncrAcc(b,i,k,q2) & VOL(q1) & INT(q2) & FRC(a,b)"
    ]
};


// console.log(events[0]);



// the aspect objects
function getObjects (height) {

    var IncrementalAccomplishment = {   "solid": [  { "x": 20,  "y": height-20},
                                                    { "x": 20,  "y": height-40}, 
                                                    { "x": 100,  "y": height-80},
                                                    { "x": 100,  "y": height-100} ],

                                    "dotted-beg": [ {"x":0, "y":height-20},
                                                    {"x":20, "y":height-20} ], 

                                    "dotted-end": [ {"x":100, "y":height-100},
                                                    {"x":120, "y":height-100} ],

                                    "bcr-labels" : {"b" : [{"x":0, "y":height-20}, {"x":-5, "y":height-20}], 
                                                    "c" : [{"x":-1, "y":height-40}, {"x":-1, "y": height-80}],
                                                    "r" : [{"x":0,  "y": height-100}, {"x":-5,  "y": height-100}]},

                                    "fd1" : {"when-first": {"x":20, "y":height-40}, "when-second": {"x":20, "y":height-20}},

                                    "fd2" : {"when-first": {"x":100, "y":height-100}, "when-second": {"x":100, "y":height-80}},

                                    "name" : "IncrAcc" 
                                };


    var NonincrementalAccomplishment = {  "solid": [    { "x": 20,  "y": height-20},
                                                        { "x": 20,  "y": height-40},
                                                        { "x": 40,  "y": height-80}, 
                                                        { "x": 60,  "y": height-40},
                                                        { "x": 80,  "y": height-80},  
                                                        { "x": 100, "y": height-40},
                                                        { "x": 100,  "y": height-100} ],

                                            "dotted-beg": [ {"x":0, "y":height-20},
                                                            {"x":20, "y":height-20} ], 

                                            "dotted-end": [ {"x":100, "y":height-100},
                                                            {"x":120, "y":height-100} ],

                                            "bcr-labels" : {"b" : [{"x":0, "y":height-20}, {"x":-5, "y":height-20}], 
                                                            "c" : [{"x":-1, "y":height-40}, {"x":-1, "y": height-80}],
                                                            "r" : [{"x":0,  "y": height-100}, {"x":-5,  "y": height-100}]},

                                            "fd1" : {"when-first": {"x":20, "y":height-40}, "when-second": {"x":20, "y":height-20}},

                                            "fd2" : {"when-first": {"x":100, "y":height-100}, "when-second": {"x":100, "y":height-40}},

                                            "name" : "NonIncrAcc"

                                        }; 

    var UndirectedEndeavor = {  "solid": [  { "x": 20,  "y": height-10},
                                            { "x": 20,  "y": height-30},
                                            { "x": 40,  "y": height-70}, 
                                            { "x": 60,  "y": height-30},
                                            { "x": 80,  "y": height-70},  
                                            { "x": 100, "y": height-30}, 
                                            { "x": 100, "y": height-10} ],

                                "dotted-beg": [ {"x":0, "y":height-10},
                                                {"x":20, "y":height-10} ], 

                                "dotted-end": [ {"x":100, "y":height-10},
                                                {"x":120, "y":height-10} ],

                                "bcr-labels" : {"b" : [{"x":0, "y":height-10}, {"x":-5, "y":height-10}], 
                                                "c" : [{"x":-1, "y":height-30}, {"x":-1, "y": height-70}],
                                                "r" : ["None"]},

                                "fd1" : {"when-first": {"x":20, "y":height-30}, "when-second": {"x":20, "y":height-10}},

                                "fd2" : {"when-first": {"x":100, "y":height-30}, "when-second": {"x":100, "y":height-10}},

                                "name" : "UndAct"

                            };

    var UndirectedActivity = {  "solid": [  { "x": 20,  "y": height-20},
                                            { "x": 40,  "y": height-60}, 
                                            { "x": 60,  "y": height-20},
                                            { "x": 80,  "y": height-60},  
                                            { "x": 100, "y": height-20} ],

                                "dotted-beg": [ {"x":0, "y":height-10},
                                                {"x":20, "y":height-10},
                                                {"x":20, "y":height-20} ], 

                                "dotted-end": [ {"x":100, "y":height-20},
                                                {"x":100, "y":height-10},
                                                {"x":120, "y":height-10} ],

                                "bcr-labels" : {"b" : [{"x":0, "y":height-10}, {"x":-5, "y":height-10}], 
                                                "c" : [{"x":-1, "y":height-20}, {"x":-1, "y": height-60}],
                                                "r" : ["None"]},

                                "fd1" : {"when-first": {"x":20, "y":height-20}, "when-second": {"x":20, "y":height-10}},

                                "fd2" : {"when-first": {"x":100, "y":height-20}, "when-second": {"x":100, "y":height-10}},

                                "name" : "UndAct"

                            }; 


    var DirectedActivity = {   		"solid": [		{ "x": 20,  "y": height-40}, 
                                                    { "x": 100,  "y": height-80} ],

                                    "dotted-beg": [ {"x":0, "y":height-20},
                                                    {"x":20, "y":height-20},
                                                    { "x": 20,  "y": height-40} ], 

                                    "dotted-end": [ {"x":100, "y":height-80} ],

                                    "bcr-labels" : {"b" : [{"x":0, "y":height-20}, {"x":-5, "y":height-20}], 
                                                    "c" : [{"x":-1, "y":height-40}, {"x":-1, "y": height-80}],
                                                    "r" : ["None"]},

                                    "fd1" : {"when-first": {"x":20, "y":height-40}, "when-second": {"x":20, "y":height-20}},

                                    "fd2" : {"when-first": {"x":100, "y":height-80}, "when-second": {"x":100, "y":height-80}},

                                    "name" : "DirAct"
                            };


    var CyclicAchievement = {   	"solid": 	[	{ "x": 47,  "y": height-20}, 
                                                    { "x": 47,  "y": height-60},
                                                    { "x": 50,  "y": height-60},
                                                    { "x": 50,  "y": height-20} ],

                                    "dotted-beg": [ {"x":0, "y":height-20},
                                                    {"x":47, "y":height-20} ], 

                                    "dotted-end": [ { "x": 50,  "y": height-20},
                                    				{ "x": 100,  "y": height-20} ],

                                    "bcr-labels" : {"b" : [{"x":0, "y":height-20}, {"x":-5, "y":height-20}], 
                                                    "c" : [{"x":-1, "y":height-20}, {"x":-1, "y": height-60}],
                                                    "r" : [{"x":0,  "y": height-60}, {"x":-5,  "y": height-60}]},

                                    "fd1" : {"when-first": {"x":47, "y":height-60}, "when-second": {"x":47, "y":height-20}},

                                    "fd2" : {"when-first": {"x":47, "y":height-60}, "when-second": {"x":47, "y":height-20}},

                                    "name" : "CycAch"
                            };


    var DirectedAchievement = {   	"solid": 	[	{ "x": 47,  "y": height-20}, 
                                                    { "x": 47,  "y": height-60} ],

                                    "dotted-beg": [ {"x":0, "y":height-20},
                                                    {"x":47, "y":height-20} ], 

                                    "dotted-end": [ { "x": 47,  "y": height-60},
                                    				{ "x": 100,  "y": height-60} ],

                                    "bcr-labels" : {"b" : [{"x":0, "y":height-20}, {"x":-5, "y":height-20}], 
                                                    "c" : [{"x":-1, "y":height-20}, {"x":-1, "y": height-60}],
                                                    "r" : [{"x":0,  "y": height-60}, {"x":-5,  "y": height-60}]},

                                    "fd1" : {"when-first": {"x":47, "y":height-60}, "when-second": {"x":47, "y":height-20}},

                                    "fd2" : {"when-first": {"x":47, "y":height-60}, "when-second": {"x":47, "y":height-20}},

                                    "name" : "DirAch" 
                            };

    //InherentState is a little trickier: it takes into account the preceding event (where profiled and points of FDs)
    //so, has two values: "extended" and "punctual"
    var InherentStateExtended = {        

                                    "solid":    [   { "x": 20,  "y": height-60}, 
                                                    { "x": 100,  "y": height-60} ],

                                    "dotted-beg": [ {"x":0, "y":height-60},
                                                    {"x":20, "y":height-60} ], 

                                    "dotted-end": [ { "x": 100,  "y": height-60},
                                                    { "x": 120,  "y": height-60} ],

                                    "bcr-labels" : {"b" : ["None"], 
                                                    "c" : ["None"],
                                                    "r" : [{"x":0,  "y": height-60}, {"x":-5,  "y": height-60}]},

                                    "fd1" : {"when-first": {"x":20, "y":height-20}, "when-second": {"x":20, "y":height-60}},

                                    "fd2" : {"when-first": {"x":100, "y":height-20}, "when-second": {"x":100, "y":height-60}},

                                    "name" : "InhStPhExt" 

                    
                                };

    var InherentStatePunctual =  {        

                                    "solid":    [   { "x": 46,  "y": height-60}, 
                                                    { "x": 48,  "y": height-60} ],

                                    "dotted-beg": [ {"x":0, "y":height-60},
                                                    {"x":46, "y":height-60} ], 

                                    "dotted-end": [ { "x": 48,  "y": height-60},
                                                    { "x": 120,  "y": height-60} ],

                                    "bcr-labels" : {"b" : ["None"], 
                                                    "c" : ["None"],
                                                    "r" : [{"x":0,  "y": height-60}, {"x":-5,  "y": height-60}]},

                                    "fd1" : {"when-first": {"x":47, "y":height-20}, "when-second": {"x":47, "y":height-60}},

                                    "fd2" : {"when-first": {"x":47, "y":height-20}, "when-second": {"x":47, "y":height-60}},

                                    "name" : "InhStPhPunct"

                                };


    var TransitoryState =   {       "solid":    [   { "x": 47,  "y": height-60}, 
                                                    { "x": 100,  "y": height-60} ],

                                    "dotted-beg": [ {"x":0, "y":height-20},
                                                    {"x":47, "y":height-20},
                                                    {"x":47, "y":height-60} ], 

                                    "dotted-end": [ { "x": 47,  "y": height-60} ],

                                    "bcr-labels" : {"b" : [{"x":0, "y":height-20}, {"x":-5, "y":height-20}], 
                                                    "c" : ["None"],
                                                    "r" : [{"x":0,  "y": height-60}, {"x":-5,  "y": height-60}]},

                                    "fd1" : {"when-first": {"x":47, "y":height-60}, "when-second": {"x":47, "y":height-20}},

                                    "fd2" : {"when-first": {"x":47, "y":height-60}, "when-second": {"x":47, "y":height-20}},

                                    "name" : "TranSt" 
                            };


    return  {   IncrAcc: IncrementalAccomplishment, 
                NonIncrAcc: NonincrementalAccomplishment, 
                UndEnd: UndirectedEndeavor,
                UndAct: UndirectedActivity ,
                DirAct: DirectedActivity,
                CycAch: CyclicAchievement,
                DirAch: DirectedAchievement,
                TranSt: TransitoryState,
                InhStPhExt: InherentStateExtended,
                InhStPhPunct: InherentStatePunctual
            };

}

//This is the accessor function 
var lineFunction = d3.line()
                          .x(function(d) { return d.x; })
                          .y(function(d) { return d.y; });


function createDiagram (svgContainer, myAspectObject) {

    var solidLine = myAspectObject["solid"];
    var dottedBeg = myAspectObject["dotted-beg"];
    var dottedEnd = myAspectObject["dotted-end"];
    var b = myAspectObject["bcr-labels"]["b"];
    var c = myAspectObject["bcr-labels"]["c"];
    var r = myAspectObject["bcr-labels"]["r"];

    var aspectName = myAspectObject["name"];

    var lineGraph = svgContainer.append("path")
                                .attr("d", lineFunction(solidLine))
                                .attr("stroke", "blue")
                                .attr("stroke-width", 2)
                                .attr("fill", "none");

    var dLinesBeg = svgContainer.append("path")
                                .attr("d", lineFunction(dottedBeg))
                                .attr("stroke", "black")
                                .style("stroke-dasharray", ("2, 2"))
                                .attr("fill", "none");

    var dLinesEnd = svgContainer.append("path")
                                .attr("d", lineFunction(dottedEnd))
                                .attr("stroke", "black")
                                .style("stroke-dasharray", ("2, 2"))
                                .attr("fill", "none");

    if (b[0]!='None') {

        var addB = svgContainer.append("path")
                            .attr("d", lineFunction(b))
                            .attr("stroke", "black")
                            .attr("stroke-width", 1)
                            .attr("fill", "none");

        var addBText = svgContainer.append("text")
                            .attr("x", b[1]["x"]-11)
                            .attr("y", b[1]["y"]+3)
                            .text('b');

        }

    if (c[0]!='None' && aspectName.indexOf("Ach")==-1) {

        var addC = svgContainer.append("path")
                            .attr("d", lineFunction(c))
                            .attr("stroke", "black")
                            .attr("stroke-width", 4)
                            .attr("fill", "none");

        var addCText = svgContainer.append("text")
                            .attr("x", c[1]["x"]-15)
                            .attr("y", (1/2)*(c[0]["y"]+c[1]["y"])+3)
                            .text('c');

        }

    if (r[0]!="None") {

        var addR = svgContainer.append("path")
                    .attr("d", lineFunction(r))
                    .attr("stroke", "black")
                    .attr("stroke-width", 1)
                    .attr("fill", "none");

        var addRText = svgContainer.append("text")
                            .attr("x", r[1]["x"]-11)
                            .attr("y", r[1]["y"]+3)
                            .text('r');
        }

}


function drawFDlines (svgContainer, myEventObject1, myEventObject2) {

    var fd1 = [myEventObject1["fd1"]["when-first"]];

    fd1.push(myEventObject2["fd1"]["when-second"]);

    var fdline1 = svgContainer.append("path")
                        .attr("d", lineFunction(fd1))
                        .attr("stroke", "red")
                        .attr("stroke-width", 1)
                        .attr("fill", "none");        


    var fd2 = [myEventObject1["fd2"]["when-first"]];

    fd2.push(myEventObject2["fd2"]["when-second"]);

    var fdline2 = svgContainer.append("path")
                        .attr("d", lineFunction(fd2))
                        .attr("stroke", "red")
                        .attr("stroke-width", 1)
                        .attr("fill", "none"); 
}


function drawPathArrows (svgContainer, myObject) {

	// here pass the second object in the causal chain to align the triangle(s)

	var x1 = myObject["fd1"]["when-second"].x;
	var y1 = myObject["fd1"]["when-second"].y;

	svgContainer.append('path')
	      .attr('d', function(d) { 
	        return 'M ' + x1 +' '+ y1 + ' l 5 5 l -10 0 z';
	      })
	      .attr("fill", "red");


	var x2 = myObject["fd2"]["when-second"].x;
	var y2 = myObject["fd2"]["when-second"].y;

	svgContainer.append('path')
	      .attr('d', function(d) { 
	        return 'M ' + x2 +' '+ y2 + ' l 5 5 l -10 0 z';
	      })
	      .attr("fill", "red");
}


function addPathForceLabels(svgContainer, subEvent1, subEvent2, prevSubEvent) {

    var x = subEvent1["fd2"]["when-first"]["x"];
    var y = (subEvent1["fd2"]["when-first"]["y"] + subEvent2["fd2"]["when-second"]["y"]) / 2;

    if (prevSubEvent[2] == 'PTH' || prevSubEvent[2] == 'FRC') {

        var thisText = prevSubEvent[2];

        var addPthFrcText = svgContainer.append("text")
                                .attr("x", x+5)
                                .attr("y", y+5)
                                .style("fill", "red")
                                .text(thisText);

    } else if (prevSubEvent[3] == 'PTH' || prevSubEvent[3] == 'FRC') {

        var thisText = prevSubEvent[3];

        var addPthFrcText = svgContainer.append("text")
                                .attr("x", x+5)
                                .attr("y", y+5)
                                .style("fill", "red")
                                .text(thisText);
    }

    else if (prevSubEvent[4] == 'PTH' || prevSubEvent[4] == 'FRC') {

        var thisText = prevSubEvent[4];

        var addPthFrcText = svgContainer.append("text")
                                .attr("x", x+5)
                                .attr("y", y+5)
                                .style("fill", "red")
                                .text(thisText);
    }

}


function drawAxes (svgContainer, height, aspectHeight, includeXaxis) {


    //hacky height is the upper part of the y-axis, while height adjusts the bottom part
    if (aspectHeight == 80) {

        var hackyHeight = height-aspectHeight+10;
        height = height;

    } else if (aspectHeight == 100) {

        var hackyHeight = height-aspectHeight-10;
        height = height-10;

    } else if (aspectHeight == 60) {

        var hackyHeight = height-aspectHeight-20;
        height = height-20;
        
    }

    if (includeXaxis) {

        var xAxis = [   {"x": 0, "y":height},
                        {"x": 120, "y":height}];

        var xline = svgContainer.append("path")
                .attr("d", lineFunction(xAxis))
                .attr("stroke", "black")
                .attr("stroke-width", 1)
                .attr("fill", "none");
    };


    var yAxis = [   {"x": 0, "y":hackyHeight},
                    {"x": 0, "y":height}];

    var yline = svgContainer.append("path")
                        .attr("d", lineFunction(yAxis))
                        .attr("stroke", "black")
                        .attr("stroke-width", 1)
                        .attr("fill", "none");
}



function addText (svgContainer, myAspectObject, subeventArray) {

    var participant = subeventArray[0];

    var strLen = participant.length*2;

    var theme = subeventArray[2];

    if (theme){
        var themeLen = theme.length*1.5;
    }
    

    var c = myAspectObject["bcr-labels"]["c"];

    var r = myAspectObject["bcr-labels"]["r"];


    if (c[0]!='None') {

        var addParticipantText = svgContainer.append("text")
                                    .attr("x", c[1]["x"]-55-strLen)
                                    .attr("y", (1/2)*(c[0]["y"]+c[1]["y"])+3)
                                    .text(participant);

    } else if (r[0]!="None") {

        var addParticipantText = svgContainer.append("text")
                                    .attr("x", r[1]["x"]-60-strLen)
                                    .attr("y", r[1]["y"]+3)
                                    .text(participant);
    }


    if (theme!==undefined && theme != 'FRC' && theme != 'PTH') {

        if (r[0]!="None") {

            var addTheme = svgContainer.append("text")
                                        .attr("x", r[1]["x"]-35-themeLen)
                                        .attr("y", r[1]["y"]-10)
                                        .text(theme);
        } else {

            var addTheme = svgContainer.append("text")
                                        .attr("x", c[1]["x"]-35-themeLen)
                                        .attr("y", (1/2)*(c[0]["y"]+c[1]["y"])-10)
                                        .text(theme);
        }

    }

}


function getHeight(allAspects) {

    // determines the height of each subevent: 60, 80, 100

    var subeventHeights = [];

    for (i in allAspects) {
        if (allAspects[i]==='IncrAcc' || allAspects[i]==='NonIncrAcc') {
            subeventHeights.push(100);
        } else if (allAspects[i]==='InhStPh') {
            subeventHeights.push(60);
        } else {
            subeventHeights.push(80);
        }
    }

    return subeventHeights;
}


function parsePredCalc (myPredCalc) {

    // form ("None" if none): [[q1PartAspectThemeFD], [q2PartAspectThemeFD], [q3PartAspectThemeFD], [q4PartAspectThemeFD], [aspectSummary]]
    var eventInfo = []

    var string_split = myPredCalc.split('&');
    var string_trim = [];

    //string_trim is the main array to iterate over
    for (i in string_split) {
        string_trim.push(string_split[i].trim());
    }

    //push q1Aspect
    var q1AspectTheme = [];
    for (i in string_trim) {

        if (string_trim[i].indexOf('Component-of(a,') !== -1) {
            var part1 = string_trim[i].split(',')[1].slice(0, -1);
            q1AspectTheme.push(part1);
        } else if (string_trim[i].indexOf('q1') !== -1) {
            var q1Instance = string_trim[i].split('(')[0];
            q1AspectTheme.push(q1Instance)
        } else if (string_trim[i].indexOf('(a,b)') !== -1) {
            var fd1Instance = string_trim[i].split('(')[0];
            q1AspectTheme.push(fd1Instance)
        }
    }
    eventInfo.push(q1AspectTheme);

    //push q2Aspect
    var q2Exists = false;
    var q2AspectTheme = [];
    for (i in string_trim) {

        if (string_trim[i].indexOf('Component-of(b,') !== -1) {
            var part2 = string_trim[i].split(',')[1].slice(0, -1);
            q2AspectTheme.push(part2);
        } else if (string_trim[i].indexOf('q2') !== -1) {
            var q2Instance = string_trim[i].split('(')[0];
            q2Exists = true;
            q2AspectTheme.push(q2Instance)
        } else if (string_trim[i].indexOf('(b,c)') !== -1) {
            var fd2Instance = string_trim[i].split('(')[0];
            q2AspectTheme.push(fd2Instance)
        }
    }
    
    if (q2Exists===false) {
        eventInfo.push("None");
    } else {
        eventInfo.push(q2AspectTheme);
    }

    //push q3aspect
    var q3Exists = false;
    var q3AspectTheme = [];
    for (i in string_trim) {

        if (string_trim[i].indexOf('Component-of(c,') !== -1) {
            var part3 = string_trim[i].split(',')[1].slice(0, -1);
            q3AspectTheme.push(part3);
        } else if (string_trim[i].indexOf('q3') !== -1) {
            var q3Instance = string_trim[i].split('(')[0];
            q3Exists = true;
            q3AspectTheme.push(q3Instance)
        } else if (string_trim[i].indexOf('(c,d)') !== -1) {
            var fd3Instance = string_trim[i].split('(')[0];
            q3AspectTheme.push(fd3Instance)
        }
    }
    
    if (q3Exists===false) {
        eventInfo.push("None");
    } else {
        eventInfo.push(q3AspectTheme);
    }


    //push q4Aspect
    var q4Exists = false;
    var q4AspectTheme = [];
    for (i in string_trim) {

        if (string_trim[i].indexOf('Component-of(d,') !== -1) {
            var part4 = string_trim[i].split(',')[1].slice(0, -1);
            q4AspectTheme.push(part4);
        } else if (string_trim[i].indexOf('q4') !== -1) {
            var q4Instance = string_trim[i].split('(')[0];
            q4Exists = true;
            q4AspectTheme.push(q4Instance)
        }
    }
    
    if (q4Exists===false) {
        eventInfo.push("None");
    } else {
        eventInfo.push(q4AspectTheme);
    }

    // form: [all aspectual types]
    // will be used to determine height of svg
    // length: number of subevents
    var aspectSummary = [];

    for (i in eventInfo) {
        if (eventInfo[i]!="None") {
            aspectSummary.push(eventInfo[i][1]);
        }
    }

    eventInfo.push(aspectSummary);

    return eventInfo;

}


function draw () {

    // var inputPredCalc = USERINPUT;

    var predcalc = events[currentEvent][6];
    
    var eventComponents = parsePredCalc(predcalc);

    // returns an array of all subevent aspect types, ex: ["UndAct", "UndAct", "IncrAcc"]
    var allAspects = eventComponents[4];

    // console.log(eventComponents);

    // this returns a 1xN array when N=number of subevents and each element is the height of the subevent, ex: [80,80,100]
    var allHeights = getHeight(allAspects);

    var svgHeight = allHeights.reduce(function(acc, val) {
        return acc + val;
    }, 0);


    //The SVG Container
    var svgContainer = d3.select(".svg-diagram").append("svg")
                                        .attr("width", 200)
                                        .attr("height", svgHeight);


    // recordObjects keeps a history of the objects for drawing of FD lines
    var recordObjects = [];


    //Start composing subevents
    for (i in allAspects) {

        var thisAspect = allAspects[i];

        // checking for extended or punctual Inherent State
        if (thisAspect === 'InhStPh') {
            if (allAspects[i-1] === 'CycAch' || allAspects[i-1] === 'DirAch') {
                thisAspect = 'InhStPhPunct';
            } else {
                thisAspect = 'InhStPhExt';
            }
        }

        // svgHeight is updated at end of for loop
        var thisHeight = svgHeight+40;

        var thisAspectHeight = allHeights[i];

        var objects = getObjects(thisHeight);

        recordObjects.push(objects)

        var thisSubevent = objects[thisAspect];


        if (i == 0) {
            var thisAxis = drawAxes(svgContainer, thisHeight, thisAspectHeight, true);
        } else {
            var secondAxis = drawAxes(svgContainer, thisHeight, thisAspectHeight, false);
        }

        var drawThisSubevent = createDiagram(svgContainer, thisSubevent);

        var subeventArray = eventComponents[i];

        var addingText = addText(svgContainer, thisSubevent, subeventArray);


        // only draw FD lines after the second subevent has been drawn
        if (i > 0) {

            var subEvent1 = recordObjects[i-1][allAspects[i-1]];


            if (allAspects[i] === 'InhStPh') {
                if (allAspects[i-1] === 'CycAch' || allAspects[i-1] === 'DirAch') {
                    var subEvent2 = objects['InhStPhPunct'];
                } else {
                    var subEvent2 = objects['InhStPhExt'];
                }
            } else {
                var subEvent2 = objects[allAspects[i]];
            }

            
            var drawForceDynamicLines = drawFDlines(svgContainer, subEvent1, subEvent2);

            // checking for PTH and drawing arrows
            var prevSubEvent = eventComponents[i-1];
            for (i in prevSubEvent) {
                if (prevSubEvent[i]==='FRC') {
                    var drawArrows = drawPathArrows(svgContainer, subEvent2);
                }
            }

            var addPthFrcLabels = addPathForceLabels(svgContainer, subEvent1, subEvent2, prevSubEvent);
            
        }

        svgHeight = svgHeight - thisAspectHeight;
    }

    // var sentence = events[currentEvent][0];
    // var themeType = events[currentEvent][3];
    // var aspectType = events[currentEvent][4];
    // var syntax = events[currentEvent][5];
    // var predicate = events[currentEvent][6];

    for (n=0; n<8; n++) {

        var labels = ['Example: ', 'VerbNet class: ', 'Argument Structure: ', 'VerbNet case frame: ', 'Force dynamics: ', 'Aspect: ', 'Predicate calculus:'];

        // if (n != 1 && n != 2) {
        if (n != 7) {
            var addedHeader = addSecondDivText(labels[n], true, n);
            var addedSentence = addSecondDivText(events[currentEvent][n], false, n);
            var addedBlank = addSecondDivText('', false, n);
        }
    }

    // generateDiagram.addEventListener('click', resetScreen);
    // generateDiagram.removeEventListener('click', draw);

}

if(typeof events[currentEvent] === 'undefined') {
    // does not exist

    var div = document.getElementById('textbox');

    div.innerHTML += '<h2>Representations for mental and social events coming soon!</h2>';   

}
else {
    // does exist
    draw()
}