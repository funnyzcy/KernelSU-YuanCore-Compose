// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 YuanCore contributors
// Optional theme layer for KernelSU; see NOTICE at the repository root.

package me.weishu.kernelsu.ui.theme.yuancore

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Shapes
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * YuanCore (元核) design tokens.
 *
 * Visual rules:
 *  - XuanQing (玄青) / XuanBai (宣白) surfaces, no hard dividers.
 *  - HunYuan indigo-violet flow is the only decorative color.
 *  - Teal is reserved for "kernel active / trusted" status.
 *  - Numbers use a monospaced face; the hero radius is 28dp.
 *
 * This object is pure data: no Android context, no repository, no side effects.
 */
object YuanCorePalette {
    val Indigo = Color(0xFF4B56F5)
    val Violet = Color(0xFF8A55F0)
    val Orchid = Color(0xFFB35AE8)
    val Teal = Color(0xFF2FD4C4)
    val Amber = Color(0xFFFFB454)
    val Rose = Color(0xFFFF6B7A)

    val Ink = Color(0xFF0B0E17)
    val InkSurface = Color(0xFF141A2B)
    val Paper = Color(0xFFF7F8FC)

    val Seed = Indigo
    val SeedArgb: Int = Indigo.toArgb()

    val Flow: List<Color> = listOf(Indigo, Violet, Orchid)
}

val YuanCoreShapes = Shapes(
    extraSmall = RoundedCornerShape(10.dp),
    small = RoundedCornerShape(14.dp),
    medium = RoundedCornerShape(20.dp),
    large = RoundedCornerShape(28.dp),
    extraLarge = RoundedCornerShape(34.dp),
)

/** Only the font face and tracking; merging this must not override weight or size. */
val YuanCoreNumeric: TextStyle = TextStyle(
    fontFamily = FontFamily.Monospace,
    letterSpacing = 0.sp,
)

object YuanCoreMotion {
    const val SPIN_MS = 9000
    const val BREATH_MS = 2600
}
