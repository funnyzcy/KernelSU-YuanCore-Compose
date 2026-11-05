// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 YuanCore contributors
// Optional theme layer for KernelSU; see NOTICE at the repository root.

package me.weishu.kernelsu.ui.theme.yuancore

import androidx.compose.material3.ColorScheme
import androidx.compose.ui.graphics.Color

/**
 * Overlay YuanCore neutral surfaces onto a scheme generated from the YuanCore
 * seed. Every semantic role (primary/onPrimary, error, fixed colors, ...) is
 * left untouched so contrast and Material3 tonal relationships stay valid.
 *
 * The seed itself is injected by the theme entry points, not here: this keeps
 * the whole tonal palette consistent instead of patching one color at a time.
 */
fun ColorScheme.yuanCore(dark: Boolean, amoled: Boolean): ColorScheme = if (dark) {
    val base = if (amoled) Color.Black else YuanCorePalette.Ink
    copy(
        background = base,
        surface = if (amoled) Color(0xFF0A0A0F) else YuanCorePalette.InkSurface,
        surfaceDim = base,
        surfaceBright = if (amoled) Color(0xFF16161F) else Color(0xFF222A40),
        surfaceContainerLowest = if (amoled) Color(0xFF050508) else Color(0xFF0E1220),
        surfaceContainerLow = if (amoled) Color(0xFF0B0B12) else Color(0xFF121829),
        surfaceContainer = if (amoled) Color(0xFF101018) else Color(0xFF161D31),
        surfaceContainerHigh = if (amoled) Color(0xFF16161F) else Color(0xFF1C243A),
        surfaceContainerHighest = if (amoled) Color(0xFF1D1D27) else Color(0xFF232C44),
        surfaceVariant = if (amoled) Color(0xFF1A1A22) else Color(0xFF202942),
        surfaceTint = YuanCorePalette.Indigo,
        scrim = Color.Black,
    )
} else {
    copy(
        background = YuanCorePalette.Paper,
        surface = Color.White,
        surfaceDim = Color(0xFFEDEFF7),
        surfaceBright = Color.White,
        surfaceContainerLowest = Color.White,
        surfaceContainerLow = Color(0xFFFBFBFE),
        surfaceContainer = Color(0xFFF5F6FB),
        surfaceContainerHigh = Color(0xFFEFF1F9),
        surfaceContainerHighest = Color(0xFFE9ECF6),
        surfaceVariant = Color(0xFFE8EBF6),
        surfaceTint = YuanCorePalette.Indigo,
    )
}
