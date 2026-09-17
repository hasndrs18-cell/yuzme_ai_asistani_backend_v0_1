"use client";

import { Float, Line, OrbitControls, Sparkles, Text } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

const laneCount = 6;
const poolLength = 18;
const poolWidth = 9;

function WaterSurface() {
  const material = useRef<THREE.ShaderMaterial>(null);
  const uniforms = useMemo(() => ({ uTime: { value: 0 } }), []);

  useFrame((_, delta) => {
    if (material.current) material.current.uniforms.uTime.value += delta;
  });

  return (
    <mesh rotation-x={-Math.PI / 2} position-y={0.05}>
      <planeGeometry args={[poolWidth, poolLength, 96, 160]} />
      <shaderMaterial
        ref={material}
        uniforms={uniforms}
        transparent
        vertexShader={`
          uniform float uTime;
          varying vec2 vUv;
          void main() {
            vUv = uv;
            vec3 transformed = position;
            transformed.z += sin(position.x * 2.4 + uTime * 1.4) * 0.025;
            transformed.z += cos(position.y * 1.7 + uTime) * 0.018;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(transformed, 1.0);
          }
        `}
        fragmentShader={`
          uniform float uTime;
          varying vec2 vUv;
          void main() {
            float shimmer = sin((vUv.x + uTime * 0.05) * 42.0) * 0.035;
            vec3 deep = vec3(0.015, 0.17, 0.22);
            vec3 glow = vec3(0.08, 0.72, 0.78);
            vec3 color = mix(deep, glow, smoothstep(0.1, 0.9, vUv.y) * 0.36 + shimmer);
            gl_FragColor = vec4(color, 0.92);
          }
        `}
      />
    </mesh>
  );
}

function LaneMarkers() {
  return (
    <group>
      {Array.from({ length: laneCount + 1 }).map((_, index) => {
        const x = -poolWidth / 2 + (index * poolWidth) / laneCount;
        return (
          <mesh key={index} position={[x, 0.09, 0]} rotation-x={-Math.PI / 2}>
            <planeGeometry args={[0.035, poolLength]} />
            <meshBasicMaterial color="#b9fbf8" transparent opacity={0.48} />
          </mesh>
        );
      })}
      {Array.from({ length: laneCount }).map((_, index) => {
        const x = -poolWidth / 2 + (index + 0.5) * (poolWidth / laneCount);
        return (
          <group key={index} position={[x, 0.13, 0]}>
            <mesh rotation-x={-Math.PI / 2}>
              <planeGeometry args={[0.12, poolLength]} />
              <meshBasicMaterial color="#ffb263" transparent opacity={0.8} />
            </mesh>
            {[-7, -3.5, 0, 3.5, 7].map((z) => (
              <mesh key={z} position={[0, 0, z]} rotation-x={-Math.PI / 2}>
                <torusGeometry args={[0.17, 0.025, 8, 20]} />
                <meshBasicMaterial color="#ffdca0" />
              </mesh>
            ))}
          </group>
        );
      })}
    </group>
  );
}

function CyberGrid({ drive }: { drive: number }) {
  const gridRef = useRef<THREE.GridHelper>(null);

  useFrame(({ clock }) => {
    if (!gridRef.current) return;
    const time = clock.getElapsedTime();
    gridRef.current.rotation.y = time * (0.012 + drive * 0.08);
    gridRef.current.scale.y = 1 + Math.sin(time * (0.8 + drive * 2)) * drive * 0.035;
  });

  return (
    <group position={[0, -0.12, 0]}>
      <gridHelper ref={gridRef} args={[18, 36, "#1d8c99", "#12424d"]} scale={[0.5, 1, 1]} />
      <mesh rotation-x={-Math.PI / 2} position-y={-0.015}>
        <planeGeometry args={[poolWidth, poolLength]} />
        <meshBasicMaterial color="#05171d" transparent opacity={0.68} />
      </mesh>
    </group>
  );
}

function CyberGravitationalAccretionRing({ drive }: { drive: number }) {
  const groupRef = useRef<THREE.Group>(null);
  const materials = useRef<THREE.MeshBasicMaterial[]>([]);
  const cool = useMemo(() => new THREE.Color("#55efff"), []);
  const hot = useMemo(() => new THREE.Color("#ff725f"), []);
  const currentColor = useMemo(() => new THREE.Color(), []);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    const time = clock.getElapsedTime();
    const speed = 0.35 + drive * 1.65;
    groupRef.current.rotation.y = time * speed;
    groupRef.current.rotation.z = Math.sin(time * 0.7) * 0.12;
    groupRef.current.scale.setScalar(0.92 + drive * 0.18 + Math.sin(time * 1.8) * 0.025);
    currentColor.lerpColors(cool, hot, drive);
    materials.current.forEach((material, index) => {
      material.color.copy(currentColor);
      material.opacity = 0.28 + drive * 0.25 - index * 0.035;
    });
  });

  return (
    <group ref={groupRef} position={[1.5, 0.52, 0]} rotation-x={Math.PI / 2.35}>
      <mesh>
        <sphereGeometry args={[0.34, 24, 24]} />
        <meshBasicMaterial color="#020409" />
      </mesh>
      {[0, 1, 2].map((index) => (
        <mesh key={index} rotation-z={index * 0.48}>
          <torusGeometry args={[0.7 + index * 0.2, 0.026 + drive * 0.018, 12, 96]} />
          <meshBasicMaterial ref={(material) => { if (material) materials.current[index] = material; }} color="#55efff" transparent opacity={0.45} toneMapped={false} />
        </mesh>
      ))}
      <pointLight color={drive > 0.65 ? "#ff725f" : "#55efff"} intensity={3 + drive * 8} distance={4} />
    </group>
  );
}

function NeonLaneLasers() {
  return (
    <group position-y={0.2}>
      {Array.from({ length: laneCount + 1 }).map((_, index) => {
        const x = -poolWidth / 2 + (index * poolWidth) / laneCount;
        return (
          <mesh key={index} position={[x, 0, 0]}>
            <boxGeometry args={[0.025, 0.035, poolLength]} />
            <meshBasicMaterial color={index % 2 ? "#66f6ff" : "#d783ff"} toneMapped={false} />
          </mesh>
        );
      })}
    </group>
  );
}

function BiometricParticles() {
  const points = useMemo(() => {
    const positions = new Float32Array(96 * 3);
    for (let index = 0; index < 96; index += 1) {
      const angle = (index / 96) * Math.PI * 2;
      const radius = 0.35 + (index % 7) * 0.045;
      positions[index * 3] = Math.cos(angle) * radius;
      positions[index * 3 + 1] = (index % 9) * 0.035;
      positions[index * 3 + 2] = Math.sin(angle) * radius;
    }
    return positions;
  }, []);
  const particleRef = useRef<THREE.Points>(null);

  useFrame(({ clock }) => {
    if (!particleRef.current) return;
    const time = clock.getElapsedTime();
    particleRef.current.rotation.y = time * 0.9;
    particleRef.current.position.y = 0.35 + Math.sin(time * 2.1) * 0.035;
  });

  return (
    <points ref={particleRef} position={[1.5, 0.35, 0]}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[points, 3]} count={points.length / 3} />
      </bufferGeometry>
      <pointsMaterial color="#b9ffff" size={0.045} transparent opacity={0.9} sizeAttenuation blending={THREE.AdditiveBlending} />
    </points>
  );
}

function Swimmer() {
  const group = useRef<THREE.Group>(null);
  useFrame(({ clock }) => {
    if (!group.current) return;
    const time = clock.getElapsedTime();
    group.current.position.z = Math.sin(time * 0.35) * 7;
    group.current.rotation.y = Math.sin(time * 1.8) * 0.05;
    group.current.rotation.x = Math.sin(time * 2.4) * 0.025;
  });

  return (
    <group ref={group} position={[1.5, 0.34, 0]}>
      <mesh rotation-z={Math.PI / 2}>
        <capsuleGeometry args={[0.13, 0.86, 8, 18]} />
        <meshStandardMaterial color="#c7faff" emissive="#176e7d" emissiveIntensity={0.7} metalness={0.55} roughness={0.25} />
      </mesh>
      <mesh position={[0.53, 0, 0]}><sphereGeometry args={[0.15, 16, 16]} /><meshBasicMaterial color="#ff5f76" toneMapped={false} /></mesh>
      {[-1, 1].map((side) => <group key={side} position={[side * 0.05, 0.04, 0]} rotation-z={side * 0.55}><mesh position={[side * 0.42, 0.2, 0]}><capsuleGeometry args={[0.045, 0.7, 6, 12]} /><meshBasicMaterial color={side > 0 ? "#ff6685" : "#66f5ff"} toneMapped={false} /></mesh><mesh position={[side * 0.78, 0.45, 0]}><sphereGeometry args={[0.06, 10, 10]} /><meshBasicMaterial color="#efffff" /></mesh></group>)}
      <Line points={[[0.32, 0.04, 0], [0, 0.1, 0], [-0.35, 0.03, 0], [-0.72, 0.1, 0]]} color="#d783ff" transparent opacity={0.85} lineWidth={1.3} />
      <Line points={[[0.05, 0, 0], [-0.9, 0.08, 0.22], [-1.8, 0.02, 0.32]]} color="#5cf6ff" transparent opacity={0.62} lineWidth={1.1} />
      <Text position={[-0.85, 0.62, 0]} fontSize={0.12} color="#ff7c91" anchorX="left">PULL / ERROR</Text>
      <Text position={[-0.86, -0.5, 0]} fontSize={0.12} color="#6cf7ff" anchorX="left">ENTRY / OPTIMAL</Text>
    </group>
  );
}

function BiomechanicalHydroJets({ drive }: { drive: number }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    const time = clock.getElapsedTime();
    groupRef.current.scale.x = 0.78 + drive * 0.55 + Math.sin(time * (3 + drive * 5)) * 0.06;
    groupRef.current.rotation.y = Math.sin(time * 1.7) * 0.035;
  });

  return (
    <group ref={groupRef} position={[1.1, 0.35, 0]}>
      <Line points={[[0, 0, 0], [-1.2, 0.05, 0.22], [-2.25, 0, 0]]} color="#55efff" transparent opacity={0.72} lineWidth={1.4} />
      <Line points={[[0, -0.04, 0], [-1.0, -0.1, -0.18], [-2.0, 0, 0]]} color="#ffb263" transparent opacity={0.5} lineWidth={1.1} />
      <Line points={[[0.05, 0.02, 0], [-0.82, 0.22, 0.08], [-1.65, 0.03, 0]]} color="#d783ff" transparent opacity={0.38} lineWidth={0.9} />
    </group>
  );
}

function OlympicRaceDisplay({ drive, timeline }: { drive: number; timeline: number }) {
  const canvas = useMemo(() => {
    const nextCanvas = document.createElement("canvas");
    nextCanvas.width = 640;
    nextCanvas.height = 360;
    return nextCanvas;
  }, []);
  const texture = useMemo(() => {
    const nextTexture = new THREE.CanvasTexture(canvas);
    nextTexture.colorSpace = THREE.SRGBColorSpace;
    return nextTexture;
  }, [canvas]);

  useFrame(({ clock }) => {
    const context = canvas.getContext("2d");
    if (!context) return;
    const time = clock.getElapsedTime();
    const phase = timeline / 100;
    const pulse = Math.sin(time * 5.5 + phase * Math.PI * 2);
    const gradient = context.createLinearGradient(0, 0, 640, 360);
    gradient.addColorStop(0, "#061b2d");
    gradient.addColorStop(0.55, "#073f55");
    gradient.addColorStop(1, "#170d31");
    context.fillStyle = gradient;
    context.fillRect(0, 0, 640, 360);
    context.fillStyle = "rgba(34, 224, 238, 0.11)";
    context.fillRect(0, 58, 640, 2);
    context.fillRect(0, 270, 640, 2);
    context.strokeStyle = "rgba(116, 249, 255, 0.34)";
    context.lineWidth = 2;
    for (let lane = 0; lane < 6; lane += 1) {
      const y = 90 + lane * 38;
      context.beginPath();
      context.moveTo(24, y);
      context.lineTo(616, y);
      context.stroke();
      const swimmerX = 68 + ((time * (58 + drive * 35) + lane * 81 + phase * 170) % 500);
      context.fillStyle = lane === 2 ? "#ffcb70" : lane % 2 ? "#6cf7ff" : "#d283ff";
      context.beginPath();
      context.ellipse(swimmerX, y - 7, 22, 5, 0, 0, Math.PI * 2);
      context.fill();
      context.fillRect(swimmerX - 16, y - 12, 8, 3);
      context.strokeStyle = "rgba(167, 255, 255, 0.45)";
      context.beginPath();
      context.moveTo(swimmerX - 30, y + 2);
      context.quadraticCurveTo(swimmerX - 48 - pulse * 5, y - 8, swimmerX - 68, y + 3);
      context.stroke();
    }
    context.fillStyle = "#ecfffa";
    context.font = "700 17px Arial";
    context.fillText("OLYMPIC HEAT / LIVE FEED", 24, 31);
    context.fillStyle = "#75fff0";
    context.font = "11px monospace";
    context.fillText(`4D FRAME ${String(Math.round(timeline)).padStart(3, "0")}  //  AQUA ARENA`, 24, 49);
    context.fillStyle = "rgba(255, 255, 255, 0.13)";
    for (let scan = 0; scan < 360; scan += 6) context.fillRect(0, scan, 640, 1);
    context.strokeStyle = "rgba(255, 127, 181, 0.7)";
    context.strokeRect(10, 10, 620, 340);
    // CanvasTexture requires an explicit upload after each canvas redraw.
    // eslint-disable-next-line react-hooks/immutability
    texture.needsUpdate = true;
  });

  return (
    <group position={[0, 2.45, -1.8]}>
      <mesh>
        <planeGeometry args={[5.6, 3.15]} />
        <meshBasicMaterial map={texture} toneMapped={false} transparent opacity={0.92} />
      </mesh>
      <mesh position={[0, 0, -0.035]}>
        <planeGeometry args={[5.82, 3.37]} />
        <meshBasicMaterial color={drive > 0.65 ? "#ff739a" : "#58efff"} wireframe transparent opacity={0.28} toneMapped={false} />
      </mesh>
      <Text position={[-2.55, -1.78, 0]} fontSize={0.12} color="#79fff1" anchorX="left">AQUA ARENA / RACE SIMULATION</Text>
    </group>
  );
}

function AstraG7({ drive, alert, focus, timeline }: { drive: number; alert: boolean; focus: "shoulder" | "wrist" | "hip" | "knee"; timeline: number }) {
  const robotRef = useRef<THREE.Group>(null);
  const headRef = useRef<THREE.Group>(null);
  const torsoRef = useRef<THREE.Mesh>(null);
  const cyan = "#62f7ff";
  const violet = "#c879ff";
  const alloy = "#b9d8dc";

  useFrame(({ clock }) => {
    if (!robotRef.current) return;
    const time = clock.getElapsedTime();
    robotRef.current.position.y = 1.02 + Math.sin(time * 1.7) * 0.08;
    robotRef.current.rotation.y = Math.sin(time * 0.48) * 0.18;
    robotRef.current.rotation.z = Math.sin(time * 1.3) * 0.025;
    if (headRef.current) { const raceLook = Math.sin(time * 1.4 + (timeline / 100) * Math.PI * 2) * 0.08; headRef.current.rotation.y = THREE.MathUtils.lerp(headRef.current.rotation.y, raceLook + (alert ? (focus === "wrist" || focus === "knee" ? -0.24 : 0.24) : 0), 0.08); headRef.current.rotation.x = Math.sin(time * 0.7) * 0.035; }
    if (torsoRef.current) torsoRef.current.scale.y = 1 + Math.sin(time * 1.9) * 0.018;
  });

  return (
    <group ref={robotRef} position={[-2.75, 1.02, 0.9]} scale={0.82}>
      <pointLight color={cyan} intensity={2.5 + drive * 4} distance={4} />
      <mesh ref={torsoRef} position={[0, 0.5, 0]}>
        <boxGeometry args={[0.68, 0.9, 0.34]} />
        <meshStandardMaterial color="#152a35" metalness={0.9} roughness={0.2} emissive="#0b5964" emissiveIntensity={0.75} />
      </mesh>
      <group ref={headRef} position={[0, 1.12, 0]}>
        <mesh>
          <icosahedronGeometry args={[0.35, 1]} />
          <meshStandardMaterial color="#1a2735" metalness={0.95} roughness={0.15} emissive="#351b59" emissiveIntensity={0.7} />
        </mesh>
      </group>
      <mesh position={[0, 1.13, 0.29]} scale={[0.72, 0.28, 0.08]}>
        <sphereGeometry args={[0.28, 20, 12]} />
        <meshBasicMaterial color={cyan} toneMapped={false} />
      </mesh>
      <mesh position={[0, 1.58, 0]}>
        <cylinderGeometry args={[0.025, 0.025, 0.25, 8]} />
        <meshBasicMaterial color={violet} toneMapped={false} />
      </mesh>
      <mesh position={[0, 1.72, 0]}>
        <sphereGeometry args={[0.06, 12, 12]} />
        <meshBasicMaterial color={cyan} toneMapped={false} />
      </mesh>
      {[-1, 1].map((side) => (
        <group key={side} position={[side * 0.5, 0.52, 0]} rotation-z={side * -0.18}>
          <mesh position={[side * 0.27, -0.28, 0]}>
            <capsuleGeometry args={[0.09, 0.42, 6, 12]} />
            <meshStandardMaterial color={alloy} metalness={0.8} roughness={0.24} emissive={violet} emissiveIntensity={0.22} />
          </mesh>
          <mesh position={[side * 0.38, -0.56, 0]}>
            <sphereGeometry args={[0.13, 12, 12]} />
            <meshBasicMaterial color={cyan} toneMapped={false} />
          </mesh>
        </group>
      ))}
      {[-1, 1].map((side) => (
        <group key={side} position={[side * 0.45, 0.82, 0]} rotation-z={side * 0.16}>
          <mesh position={[side * 0.28, -0.18, 0]}>
            <capsuleGeometry args={[0.08, 0.38, 6, 12]} />
            <meshStandardMaterial color={alloy} metalness={0.85} roughness={0.2} emissive={cyan} emissiveIntensity={0.3} />
          </mesh>
          <mesh position={[side * 0.4, -0.38, 0]}>
            <sphereGeometry args={[0.1, 12, 12]} />
            <meshBasicMaterial color={violet} toneMapped={false} />
          </mesh>
        </group>
      ))}
      <mesh position={[0, 0.51, -0.23]}>
        <torusGeometry args={[0.29, 0.025, 8, 32]} />
        <meshBasicMaterial color={violet} toneMapped={false} transparent opacity={0.8} />
      </mesh>
      <mesh position={[0, 0.64, 0.21]} rotation-x={Math.PI / 2}>
        <torusGeometry args={[0.46, alert ? 0.035 : 0.018, 8, 48]} />
        <meshBasicMaterial color={alert ? "#ff596e" : cyan} transparent opacity={alert ? 0.82 : 0.36} toneMapped={false} />
      </mesh>
      <Text position={[-0.62, -0.82, 0]} fontSize={0.16} color={cyan} anchorX="left">ASTRA-G7</Text>
    </group>
  );
}

function CameraDrift() {
  useFrame(({ camera, clock }) => {
    const time = clock.getElapsedTime();
    camera.position.x = THREE.MathUtils.lerp(camera.position.x, Math.sin(time * 0.12) * 2.4, 0.015);
    camera.position.y = THREE.MathUtils.lerp(camera.position.y, 7.2 + Math.sin(time * 0.16) * 0.45, 0.015);
    camera.lookAt(0, 0, 0);
  });
  return null;
}

export default function SwimPoolCanvas({ heartRate, cssPaceSeconds, timeline, robotSignal }: { heartRate: number; cssPaceSeconds: number; timeline: number; robotSignal: { alert: boolean; focus: "shoulder" | "wrist" | "hip" | "knee" } }) {
  const heartDrive = THREE.MathUtils.clamp((heartRate - 110) / 70, 0, 1);
  const paceDrive = THREE.MathUtils.clamp(1 - Math.abs(cssPaceSeconds - 92) / 24, 0, 1);
  const drive = THREE.MathUtils.clamp(heartDrive * 0.45 + paceDrive * 0.55, 0, 1);

  return (
    <div className="pool-canvas" aria-label="İnteraktif 3D yüzme havuzu">
      <div className="pool-fallback" aria-hidden="true"><div className="fallback-ring ring-a" /><div className="fallback-ring ring-b" /><div className="fallback-ring ring-c" /><div className="fallback-grid" /><div className="fallback-swimmer" /></div>
      <Canvas onCreated={({ gl }) => { gl.domElement.addEventListener("webglcontextlost", () => { gl.domElement.dataset.contextLost = "true"; }, { once: true }); }} camera={{ position: [0, 7.2, 10.5], fov: 42 }} dpr={1} gl={{ antialias: false, powerPreference: "low-power" }}>
        <color attach="background" args={["#071014"]} />
        <fog attach="fog" args={["#071014", 9, 25]} />
        <ambientLight intensity={1.2} color="#9ff8f4" />
        <directionalLight position={[3, 8, 4]} intensity={2.4} color="#fff4df" />
        <pointLight position={[-5, 3, -5]} intensity={16} distance={16} color="#ff725f" />
        <pointLight position={[5, 2, 5]} intensity={14} distance={14} color="#35d9e2" />
        <WaterSurface />
        <CyberGrid drive={drive} />
        <LaneMarkers />
        <NeonLaneLasers />
        <OlympicRaceDisplay drive={drive} timeline={timeline} />
        <BiomechanicalHydroJets drive={drive} />
        <AstraG7 drive={drive} alert={robotSignal.alert} focus={robotSignal.focus} timeline={timeline} />
        <Swimmer />
        <BiometricParticles />
        <Float speed={1.5} rotationIntensity={0.08} floatIntensity={0.25}>
          <Text position={[-3.85, 1.2, -5.8]} rotation={[-0.38, 0, 0]} fontSize={0.28} color="#a8ffff" anchorX="left">
            CYBER POOL / LIVE
          </Text>
        </Float>
        <Sparkles count={80} scale={[12, 3, 20]} size={1.4} speed={0.2} color="#86f5ed" />
        <CameraDrift />
        <OrbitControls enablePan={false} minDistance={8} maxDistance={15} maxPolarAngle={Math.PI / 2.1} />
      </Canvas>
    </div>
  );
}