difference(){
union(){
translate([48,55,0])cube([25,100,7],center=true);
translate([25.5,20,0])cube([70,42,7],center=true);
translate([58,95,20])cube([5,20,45],center=true);
translate([58,60,20])cube([5,20,45],center=true);
}
translate([-15,20,13])rotate([0,90,0])cylinder(d=27,h=100,$fn=100);
translate([53,95,14])
hull(){
    rotate([0,90,0])cylinder(d=5.7,h=10,$fn=80);
translate([0,0,22])rotate([0,90,0])cylinder(d=5.7,h=10,$fn=80);    
}
translate([53,60,14])
hull(){
    rotate([0,90,0])cylinder(d=5.7,h=10,$fn=80);
translate([0,0,22])rotate([0,90,0])cylinder(d=5.7,h=10,$fn=80);    
}
translate([30,4,-10]){
cylinder(d=3.5,h=20,$fn=50);
translate([0,32,0])cylinder(d=3.5,h=20,$fn=50);
}
}


