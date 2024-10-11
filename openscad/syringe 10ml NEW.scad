//Change these values according to your syringe
//Following values are for our 10 ml syringe
d_piston=16.6;
d_plunger=14;
d_syringeholder=32.2;
d_syringe=16.6;
h_syringegroove=4.1;


//other parameters
depthsiringehole=2;
thickness=8;
cut=thickness+2;
thickness2=15; //thickness pushing structure
cut2=thickness2+20; 
r_axis=4.3; //8mm axis
width=95; //width of first and last pieces
height=50;//motor basement
height2=30;//syringe end blocker
d_M3=3.5;
d_M4=4.5;
d_endsyringe=11;//diameter for syringe end (luer lock pass thru)
r_M8_nut=7.9;
h_M8_nut=7.1;
d_M3_nut=6.5;
h_M3_nut=3;
r_LM8UU=8;
lung=30;



//follows calculations
r_piston=d_piston/2;
r_plunger=d_plunger/2;
r_syringeholder=d_syringeholder/2;
r_syringe=d_syringe/2;


//=== syringe central holder
translate([0,0,90]){
rotate([0,0,-90]){
translate ([0,30,0]) {
difference(){
union(){
translate([5,0,0]) cube([lung,16,thickness2],center=true);
cylinder(h=thickness2,r=8, center=true, $fn=100);
}
translate([-10,0,0]) cube([20,1,thickness2+4],center=true);
cylinder(h=lung,r=r_axis, center=true, $fn=100);
translate([-7,0,0]) rotate([90,0,0]) cylinder(h=lung,d=d_M3, center=true, $fn=100);
}
}
translate ([0,-30.0]){
difference(){
union(){
translate([5,0,0]) cube([lung,16,thickness2],center=true);
cylinder(h=thickness2,r=8, center=true, $fn=100);
}
translate([-10,0,0]) cube([20,1,thickness2+4],center=true);
cylinder(h=lung,r=r_axis, center=true, $fn=100);
translate([-7,0,0]) rotate([90,0,0]) cylinder(h=lung,d=d_M3, center=true, $fn=100);
}
}

 }
difference () {
rotate([0,0,-90])  translate ([41/2+3,0,0])cube([41-6,76,thickness2],center=true);
//bevels
translate([46,-47.5,0]) rotate([0,0,60]) cube([40,40,cut2],center=true);
translate([-46,-47.5,0]) rotate([0,0,30]) cube([40,40,cut2],center=true);
//syringe groove
translate([0,0,-depthsiringehole]){
translate([0,-30,0])cylinder(h=h_syringegroove,r=r_syringeholder, center=true, $fn=100); 
translate([0,-30-r_syringeholder,0]) cube([r_syringeholder*2,r_syringeholder*2,h_syringegroove],center=true); 
translate([0,-30,depthsiringehole])cylinder(h=(thickness2+depthsiringehole)*2,r=r_syringe, center=true, $fn=100);
translate([0,-30-r_syringeholder,depthsiringehole]) cube([r_syringe*2,r_syringeholder*2,(thickness2+depthsiringehole)*2],center=true);   
    }
}

}



//------------------
//syringe end block holder
//------------------
translate([0,0,130])rotate([0,180,0]){
    
difference(){
hull(){    
    translate([0,-30,0])cylinder(d=d_endsyringe+thickness,h=thickness,$fn=80,center=true); 
translate([0,height/2-31/2-10-(height2-height)/2,0])cube([width,height2,thickness],center=true);
}
//holes for axis
translate([30,0,0])cylinder(h=cut,r=r_axis, center=true, $fn=100);
translate([-30,0,0])cylinder(h=cut,r=r_axis, center=true, $fn=100);    

//hole for central screw
cylinder(h=cut,r=r_axis+0.3, center=true, $fn=100);

//hole for syringe end
    translate([0,-30,0])cylinder(d=d_endsyringe,h=cut,$fn=80,center=true);    
}
//supports


translate([width/2-7.5,height/2-6.5,0])support(); 
translate([-width/2+7.5,height/2-6.5,0])support(); 
}


//------------------
//pushing structure
//------------------
translate([0,0,50])rotate([0,180,0])
difference(){
cube([82,85,thickness2],center=true);
    
    //difference

cylinder(h=40,r=r_axis+0.1, center=true, $fn=100);
rotate([0,0,30]) cylinder(h=h_M8_nut,r=r_M8_nut, center=true, $fn=6);
translate([0,10,0]) cube([r_M8_nut*2-1.5,20,h_M8_nut],center=true);

//LM8UU holes
translate([30,0,-15])cylinder(h=60,r=r_LM8UU, center=true, $fn=100);
translate([-30,0,-15])cylinder(h=60,r=r_LM8UU, center=true, $fn=100);

translate([0,51,0]) cube([130,80,80],center=true);

//bevels
translate([45,-47.5,0]) rotate([0,0,45]) cube([40,40,cut2],center=true);
translate([-45,-47.5,0]) rotate([0,0,45]) cube([40,40,cut2],center=true);

//piston groove
translate([0,0,-depthsiringehole]){
translate([0,-30,0])cylinder(h=h_syringegroove,r=r_piston, center=true, $fn=100); 
translate([0,-30-r_piston,0]) cube([r_piston*2,r_piston*2,h_syringegroove],center=true);        
translate([0,-30,-(thickness2-depthsiringehole)/2])cylinder(h=thickness2-depthsiringehole,r=r_plunger, center=true, $fn=100);
translate([0,-30-r_piston,-(thickness2-depthsiringehole)/2]) cube([r_plunger*2,r_piston*2,thickness2-depthsiringehole],center=true);   

//screws 
    
translate([0,-29.5,(thickness2-depthsiringehole)/2])cylinder(h=thickness2-depthsiringehole,d=d_M3, center=true, $fn=100);
 
//M3 nuts
color([1,0,0])translate([0,-29.5,depthsiringehole+h_M3_nut/2])  cube ([d_M3_nut,10,h_M3_nut], true);


}
}


//------------------
//NEMA17 holder
//------------------
difference()
{
translate([0,height/2-31/2-10,0])cube([width,height,thickness],center=true);
//holes for axis
translate([30,0,0])cylinder(h=cut,r=r_axis, center=true, $fn=100);
translate([-30,0,0])cylinder(h=cut,r=r_axis, center=true, $fn=100);

//holes for NEMA 17    
translate([31/2,31/2,0])cylinder(d=d_M3,h=cut,center=true,$fn=30);    
translate([-31/2,31/2,0])cylinder(d=d_M3,h=cut,center=true,$fn=30);    
    translate([31/2,-31/2,0])cylinder(d=d_M3,h=cut,center=true,$fn=30);    
translate([-31/2,-31/2,0])cylinder(d=d_M3,h=cut,center=true,$fn=30);  
//NEMA 17 central hole    
 cylinder(d=24,h=cut,center=true,$fn=80);     
}
//supports

translate([width/2-7.5,height/2-6.5,0])support();    
translate([-width/2+7.5,height/2-6.5,0])support();      
    
translate([30,0,-thickness-5])blocco();
translate([-30,0,-thickness-5])blocco();    
translate([30,0,thickness+5])blocco();
translate([-30,0,thickness+5])blocco();
translate([30,0,130-thickness-5])blocco();
translate([-30,0,130-thickness-5])blocco();    
translate([30,0,130+thickness+5])blocco();
translate([-30,0,130+thickness+5])blocco();       
translate([-30,0,29])rotate([0,0,-90]) bloccoendstop();    
 

module blocco(){
        rotate([0,0,90])
difference(){
union(){
translate([-6,0,0]) cube([12,16,thickness],center=true);
cylinder(h=thickness,r=8, center=true, $fn=100);
}
translate([-10,0,0]) cube([20,1,cut],center=true);
cylinder(h=cut,r=r_axis, center=true, $fn=100);
translate([-7,0,0]) rotate([90,0,0]) cylinder(h=cut*2,d=d_M3, center=true, $fn=100);
}
}

module bloccoendstop(){
    height=8;
difference(){
union(){
translate([-6,0,0]) cube([12,16,height],center=true);
cylinder(h=height,r=8, center=true, $fn=100);
}
translate([-10,0,0]) cube([20,1,height+4],center=true);
cylinder(h=30,r=r_axis, center=true, $fn=100);
translate([-7,0,0]) rotate([90,0,0]) cylinder(h=30,d=d_M3, center=true, $fn=100);
}
translate([8,0,0])cube([5,10,height],center=true);
translate([0,8,0])
difference(){
    union(){
translate([12,-7.5,8-height/2])cube([4,30,16],center=true);
translate([14,-18,-4])cube([4,2,16]);
    translate([14,1,-4])cube([4,2,16]); 
    }
translate([2,-17,9])rotate([0,90,0])cylinder(d=d_M3,h=20,$fn=40);
translate([2,2,9])rotate([0,90,0])cylinder(d=d_M3,h=20,$fn=40);
    }
}


module support(){
translate([0,0,14]){
difference(){    
cube([15,12,20],center=true);
//difference
translate([0,0,-2.5])rotate([90,0,0])cylinder(d=d_M4,h=40,$fn=50,center=true);    
}    
 translate([15/2-1,-6,9])
hull(){
cube([1,1,1]);    
translate([0,-3,-20])cube([1,4,1]);        
}    
 translate([-15/2,-6,9])
hull(){
cube([1,1,1]);    
translate([0,-3,-20])cube([1,4,1]);        
}    
}
}