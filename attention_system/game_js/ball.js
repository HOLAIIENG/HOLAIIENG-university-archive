/*
todo: make it look good, not in this file
*/

function Ball(pos){
    this.pos = pos;
    this.gravity = 50;

    this.rotVel = 0;
    this.rotAxis = [0,0,0];
    this.rotMat = I();

    this.yFriction = 0.3;
    this.xFriction = 0.5;

    this.velocity = [0,0,0];
    // desired size (may be clamped to a minimum to avoid physics instability)
    this.size = 0.1;
    this.minSize = 0.05;
    if(this.size < this.minSize){
        console.warn("Ball size too small, clamping to minSize:", this.minSize);
        this.size = this.minSize;
    }

    this.onGround = () => {
        // threshold scaled with size to avoid incorrect ground detection for very small balls
        let thresh = Math.max(0.02, this.size * 0.5);
        return de(plus(this.pos, [0, -this.size, 0])) < thresh;
    }

    this.update = () => {
        if(de(this.pos) <= this.size){
            this.velocity = times(reflect(this.velocity, deNormal(this.pos)), 1);
            this.velocity[1] *= 1-this.yFriction;
            // avoid dividing by an extremely small size
            this.rotVel = -Math.hypot(this.velocity[0], this.velocity[2]) / Math.max(this.size, 0.01);
            this.rotAxis = (cross(normalize([this.velocity[0], 0, this.velocity[2]]), [0, 1, 0]));
        }

        // project out of geometry if penetrating; limit iterations to avoid infinite loops
        let iter = 0;
        while(de(this.pos) < this.size && iter < 10){
            this.pos = plus(this.pos, times(deNormal(this.pos), -(de(this.pos) - this.size)));
            iter++;
        }

        if(this.onGround() && abs(this.velocity[1]) < 0.5){
            this.velocity[1] = 0;
            this.velocity[0] *= 1-this.xFriction*dt;
            this.velocity[2] *= 1-this.xFriction*dt;

            this.rotVel = -Math.hypot(this.velocity[0], this.velocity[2]) / Math.max(this.size, 0.01);
            this.rotAxis = (cross(normalize([this.velocity[0], 0, this.velocity[2]]), [0, 1, 0]));

        } else {
            this.velocity = plus(this.velocity, [0, -this.gravity * dt, 0]);
        }
        this.pos = plus(this.pos, times(this.velocity, dt));

        this.rotAxis = (cross(normalize([this.velocity[0], 0, this.velocity[2]]), [0, 1, 0]));

        this.rotMat = matTimesMat(rotAxisMat(this.rotVel*dt, this.rotAxis), this.rotMat);



        this.updateUniforms();
    }

    this.updateUniforms = () => {
        renderer.setUni("ballPos", this.pos);
        renderer.setUni("ballRotMat", this.rotMat);
        // keep shader informed of the ball radius so rendering matches physics
        renderer.setUni("ballSize", this.size);
    }

    this.de = (p) => {
        return len(plus(p, times(this.pos, -1))) - this.size;
    }
}

let ball = new Ball([0, 10, 0]);