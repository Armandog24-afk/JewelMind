import type * as THREE from 'three'

interface ComponentMeshProps {
  geometry: THREE.BufferGeometry
  color: string
  opacity?: number
  metalness?: number
  roughness?: number
}

export function ComponentMesh({
  geometry,
  color,
  opacity = 1,
  metalness = 0.65,
  roughness = 0.35,
}: ComponentMeshProps) {
  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial
        color={color}
        transparent={opacity < 1}
        opacity={opacity}
        metalness={metalness}
        roughness={roughness}
      />
    </mesh>
  )
}
