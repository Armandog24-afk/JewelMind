import type * as THREE from 'three'

interface ComponentMeshProps {
  geometry: THREE.BufferGeometry
  color: string
  opacity?: number
  metalness?: number
  roughness?: number
  transmission?: number
  ior?: number
  thickness?: number
  clearcoat?: number
  envMapIntensity?: number
  emissive?: string
  emissiveIntensity?: number
}

/**
 * Renders one Atlas component's already-tessellated preview mesh. Always
 * `meshPhysicalMaterial` (a superset of the standard material) so both
 * Technical mode's plain metal/stone look and Presentation mode's
 * transmissive stone look share one material type — see
 * docs/bible/10-vision/231-material-system.md. Passing no
 * transmission/clearcoat leaves it behaving exactly like a standard PBR
 * material.
 */
export function ComponentMesh({
  geometry,
  color,
  opacity = 1,
  metalness = 0.65,
  roughness = 0.35,
  transmission = 0,
  ior = 1.5,
  thickness = 0,
  clearcoat = 0,
  envMapIntensity = 1,
  emissive = '#000000',
  emissiveIntensity = 0,
}: ComponentMeshProps) {
  return (
    <mesh geometry={geometry} castShadow receiveShadow>
      <meshPhysicalMaterial
        color={color}
        transparent={opacity < 1 || transmission > 0}
        opacity={opacity}
        metalness={metalness}
        roughness={roughness}
        transmission={transmission}
        ior={ior}
        thickness={thickness}
        clearcoat={clearcoat}
        envMapIntensity={envMapIntensity}
        emissive={emissive}
        emissiveIntensity={emissiveIntensity}
      />
    </mesh>
  )
}
