renderer.addUniform("res", "vec2", [window.innerWidth, window.innerHeight]);

renderer.addUniform("camPos", "vec3", [0,5,0]);

renderer.addUniform("camAngle", "vec2", [0,0]);

renderer.addUniform("t", "float", 0);

renderer.addUniform("ballPos", "vec3", [0,0,0]);

renderer.addUniform("ballAngle", "vec2", [0,0]);

renderer.addUniform("playerPos", "vec3", [0,0,0]);

renderer.addUniform("playerAngle", "vec2", [0,0]);

renderer.addUniform("ballRotMat", "mat3", I());
renderer.addUniform("ballSize", "float", ball.size);
// visual tuning uniforms: margin to expand the solid pixel region and final opacity
renderer.addUniform("ballSolidMargin", "float", 0.02);
renderer.addUniform("ballOpacity", "float", 1.0);

renderer.draw();

let t = performance.now()/1000;
let dt = 1/120;

function update(){
    try{
        dt = performance.now() / 1000 - t;
        if(dt > 1/20){
            dt = 1/120;
        }
    
        t = performance.now()/1000;

        player.update();

        ball.update();
    
        renderer.setUni("t", t);
        renderer.draw();
    
        keyPressed = [];
        mousePressed = [];
    } catch(e) {
        console.log(e);
    }
    requestAnimationFrame(update);
}

update();