"""Gem visual material profiles (brief sections 13/22).

THE STANDING DISCLAIMER FOR THIS ENTIRE MODULE: every number here is a
RENDERING PARAMETER chosen to make a stone look plausible on screen. None is a
measurement, and none may ever be presented as one.

`ior` in particular is the value a renderer is handed, not the gem's refractive
index as a laboratory would report it. `dispersion` drives a sparkle effect
rather than describing real spectral separation. Colours are stylized, not
spectral. This is `PRELIMINARY` rendering data throughout (GEM-GOV-007).

Profiles are separate from gem identity on purpose (brief section 13): a pale
sapphire and a deep blue one share an identity and differ in appearance, so a
user must be able to change how a stone looks without changing what it is.
"""

from __future__ import annotations

from jewelmind.gem.models import FALLBACK_VISUAL_PROFILE_ID, GemVisualProfile

#: Version of this profile set. Bumped on any change to a rendering parameter,
#: so a generated artifact can identify which appearance it was made with
#: (brief section 28).
VISUAL_PROFILE_SET_VERSION = "1.0.0"


def _profile(**kwargs) -> GemVisualProfile:
    return GemVisualProfile(**kwargs)


#: The generic fallback. Used whenever a gem has no profile of its own — an
#: unknown gem, a custom gem, or an entry whose profile reference does not
#: resolve.
#:
#: It is deliberately NEUTRAL rather than diamond-like. Falling back to a
#: brilliant white stone would make an unidentified gem look like the most
#: valuable possible interpretation of itself, which is the one appearance a
#: fallback must never have.
FALLBACK_PROFILE = _profile(
    profileId=FALLBACK_VISUAL_PROFILE_ID,
    renderCategory="FALLBACK",
    baseColor="#c9ccd1",
    metalness=0.0,
    roughness=0.25,
    opacity=0.85,
    transmission=0.35,
    ior=1.5,
    thickness=0.6,
    clearcoat=0.2,
    envMapIntensity=0.8,
    dispersion=0.0,
    isFallback=True,
    description=(
        "Neutral generic gem appearance used when a gem has no profile of its "
        "own. Deliberately not diamond-like, so an unidentified stone is never "
        "rendered as the most valuable reading of itself."
    ),
)

_ENTRIES: list[GemVisualProfile] = [
    FALLBACK_PROFILE,
    # ------------------------------------------------ transparent, colourless
    _profile(
        profileId="colourless.brilliant",
        renderCategory="TRANSPARENT_BRILLIANT",
        baseColor="#f2f8ff",
        roughness=0.02, opacity=1.0, transmission=0.95, ior=2.4,
        thickness=1.2, clearcoat=1.0, envMapIntensity=1.5, dispersion=0.85,
        description=(
            "High-sparkle colourless transparent look. A stylized bright-stone "
            "appearance, not a model of diamond optics."
        ),
    ),
    _profile(
        profileId="colourless.moderate",
        renderCategory="TRANSPARENT_BRILLIANT",
        baseColor="#f0f4f8",
        roughness=0.05, opacity=1.0, transmission=0.9, ior=1.8,
        thickness=1.0, clearcoat=0.6, envMapIntensity=1.2, dispersion=0.35,
        description=(
            "Colourless transparent look with less sparkle than the brilliant "
            "profile. Used for colourless stones that read as glassier."
        ),
    ),
    # ------------------------------------------------- transparent, coloured
    _profile(
        profileId="red.deep",
        renderCategory="TRANSPARENT_COLOURED",
        baseColor="#9b1128",
        roughness=0.04, opacity=1.0, transmission=0.72, ior=1.77,
        thickness=1.4, clearcoat=0.8, envMapIntensity=1.2, dispersion=0.12,
        description="Deep saturated red transparent appearance for ruby-class stones.",
    ),
    _profile(
        profileId="blue.deep",
        renderCategory="TRANSPARENT_COLOURED",
        baseColor="#123c8c",
        roughness=0.04, opacity=1.0, transmission=0.72, ior=1.77,
        thickness=1.4, clearcoat=0.8, envMapIntensity=1.2, dispersion=0.12,
        description="Deep saturated blue transparent appearance for sapphire-class stones.",
    ),
    _profile(
        profileId="green.deep",
        renderCategory="TRANSPARENT_COLOURED",
        baseColor="#0f7a4a",
        roughness=0.08, opacity=1.0, transmission=0.62, ior=1.58,
        thickness=1.5, clearcoat=0.5, envMapIntensity=1.0, dispersion=0.08,
        description=(
            "Deep green transparent appearance for emerald-class stones, with a "
            "slightly higher roughness than corundum-class profiles."
        ),
    ),
    _profile(
        profileId="green.light",
        renderCategory="TRANSPARENT_COLOURED",
        baseColor="#9bc53d",
        roughness=0.05, opacity=1.0, transmission=0.78, ior=1.65,
        thickness=1.1, clearcoat=0.6, envMapIntensity=1.1, dispersion=0.1,
        description="Light yellow-green transparent appearance for peridot-class stones.",
    ),
    _profile(
        profileId="blue.pale",
        renderCategory="TRANSPARENT_COLOURED",
        baseColor="#a8dbe8",
        roughness=0.05, opacity=1.0, transmission=0.85, ior=1.58,
        thickness=1.0, clearcoat=0.6, envMapIntensity=1.1, dispersion=0.08,
        description="Pale blue transparent appearance for aquamarine-class stones.",
    ),
    _profile(
        profileId="violet.medium",
        renderCategory="TRANSPARENT_COLOURED",
        baseColor="#7a4fb5",
        roughness=0.05, opacity=1.0, transmission=0.8, ior=1.55,
        thickness=1.1, clearcoat=0.6, envMapIntensity=1.1, dispersion=0.08,
        description="Medium violet transparent appearance for amethyst-class stones.",
    ),
    _profile(
        profileId="yellow.warm",
        renderCategory="TRANSPARENT_COLOURED",
        baseColor="#e0a12c",
        roughness=0.05, opacity=1.0, transmission=0.82, ior=1.55,
        thickness=1.1, clearcoat=0.6, envMapIntensity=1.1, dispersion=0.09,
        description="Warm yellow transparent appearance for citrine-class stones.",
    ),
    _profile(
        profileId="pink.medium",
        renderCategory="TRANSPARENT_COLOURED",
        baseColor="#e0719a",
        roughness=0.05, opacity=1.0, transmission=0.8, ior=1.62,
        thickness=1.1, clearcoat=0.7, envMapIntensity=1.1, dispersion=0.1,
        description="Medium pink transparent appearance for pink tourmaline-class stones.",
    ),
    _profile(
        profileId="orange.warm",
        renderCategory="TRANSPARENT_COLOURED",
        baseColor="#c4581f",
        roughness=0.05, opacity=1.0, transmission=0.74, ior=1.75,
        thickness=1.2, clearcoat=0.7, envMapIntensity=1.1, dispersion=0.14,
        description="Warm orange-red transparent appearance for spessartine-class garnets.",
    ),
    _profile(
        profileId="brown.warm",
        renderCategory="TRANSPARENT_COLOURED",
        baseColor="#8a4b2a",
        roughness=0.06, opacity=1.0, transmission=0.7, ior=1.62,
        thickness=1.2, clearcoat=0.5, envMapIntensity=1.0, dispersion=0.08,
        description="Warm brown transparent appearance for topaz- and zircon-class stones.",
    ),
    # ------------------------------------------------------------ translucent
    _profile(
        profileId="translucent.green",
        renderCategory="TRANSLUCENT",
        baseColor="#4f8f6b",
        roughness=0.22, opacity=1.0, transmission=0.32, ior=1.66,
        thickness=2.0, clearcoat=0.25, envMapIntensity=0.7, dispersion=0.0,
        description="Waxy translucent green appearance for jade-class materials.",
    ),
    _profile(
        profileId="translucent.warm",
        renderCategory="TRANSLUCENT",
        baseColor="#d69a3c",
        roughness=0.3, opacity=1.0, transmission=0.4, ior=1.54,
        thickness=1.8, clearcoat=0.2, envMapIntensity=0.6, dispersion=0.0,
        description="Warm translucent appearance for amber-class organic materials.",
    ),
    # ---------------------------------------------------------------- opaque
    _profile(
        profileId="opaque.turquoise",
        renderCategory="OPAQUE",
        baseColor="#41b3b8",
        roughness=0.45, opacity=1.0, transmission=0.0, ior=1.61,
        thickness=0.0, clearcoat=0.15, envMapIntensity=0.5, dispersion=0.0,
        description="Matte opaque blue-green appearance for turquoise-class materials.",
    ),
    _profile(
        profileId="opaque.coral",
        renderCategory="OPAQUE",
        baseColor="#d95f52",
        roughness=0.4, opacity=1.0, transmission=0.0, ior=1.5,
        thickness=0.0, clearcoat=0.2, envMapIntensity=0.5, dispersion=0.0,
        description="Matte opaque red-orange appearance for coral-class organic materials.",
    ),
    # ---------------------------------------------------- variable appearance
    _profile(
        profileId="iridescent.opal",
        renderCategory="IRIDESCENT",
        baseColor="#dfe9f2",
        roughness=0.15, opacity=1.0, transmission=0.45, ior=1.45,
        thickness=1.4, clearcoat=0.5, envMapIntensity=1.0, dispersion=0.5,
        hasVariableColour=True,
        description=(
            "Approximation of an opal-like appearance. Play-of-colour is NOT "
            "simulated; hasVariableColour records that this is a known "
            "approximation rather than a faithful render."
        ),
    ),
    _profile(
        profileId="pearlescent.white",
        renderCategory="PEARLESCENT",
        baseColor="#f4ece1",
        metalness=0.15, roughness=0.18, opacity=1.0, transmission=0.0,
        ior=1.53, thickness=0.0, clearcoat=0.7, envMapIntensity=1.1,
        dispersion=0.0, hasVariableColour=True,
        description=(
            "Soft pearlescent surface appearance. A pearl's orient is NOT "
            "simulated; hasVariableColour records the approximation."
        ),
    ),
    # ---------------------------------------------------- moonstone / adular
    _profile(
        profileId="translucent.moonstone",
        renderCategory="TRANSLUCENT",
        baseColor="#dfe6ef",
        roughness=0.12, opacity=1.0, transmission=0.5, ior=1.52,
        thickness=1.5, clearcoat=0.4, envMapIntensity=0.9, dispersion=0.0,
        hasVariableColour=True,
        description=(
            "Translucent white-blue appearance for moonstone-class materials. "
            "Adularescence is NOT simulated; the flag records the approximation."
        ),
    ),
]

GEM_VISUAL_PROFILES: dict[str, GemVisualProfile] = {
    entry.profileId: entry for entry in _ENTRIES
}


def get_visual_profile(profile_id: str | None) -> GemVisualProfile:
    """Resolve a profile ID, falling back to the generic profile.

    Never raises. An unresolvable reference is a real possibility — a saved
    project may name a profile that has since been removed — and the correct
    response is a safe generic appearance plus an observable fallback flag on
    `ResolvedGem`, not a crash and not a silent substitution of some other
    gem's look (brief section 22).
    """

    if profile_id is None:
        return FALLBACK_PROFILE
    return GEM_VISUAL_PROFILES.get(profile_id, FALLBACK_PROFILE)


def profile_exists(profile_id: str) -> bool:
    return profile_id in GEM_VISUAL_PROFILES
