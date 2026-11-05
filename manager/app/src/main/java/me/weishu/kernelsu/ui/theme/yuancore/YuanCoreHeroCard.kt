// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 YuanCore contributors
// Optional theme layer for KernelSU; see NOTICE at the repository root.

package me.weishu.kernelsu.ui.theme.yuancore

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicText
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import me.weishu.kernelsu.ui.theme.isInDarkTheme

/**
 * Hero status card shared by both Home implementations. It deliberately does
 * not read either shell's color scheme so it renders identically in Material
 * and Miuix mode.
 */
@Composable
fun YuanCoreHeroCard(
    title: String,
    subtitle: String,
    active: Boolean,
    badge: String,
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
) {
    val gradient = Brush.linearGradient(
        colors = if (isInDarkTheme()) {
            listOf(Color(0xFF1B2050), Color(0xFF321E5C), Color(0xFF101528))
        } else {
            YuanCorePalette.Flow
        },
    )
    val shape = RoundedCornerShape(28.dp)
    var cardModifier = modifier
        .fillMaxWidth()
        .clip(shape)
        .background(gradient)
    if (onClick != null) {
        cardModifier = cardModifier.clickable(onClick = onClick)
    }

    Row(
        modifier = cardModifier.padding(horizontal = 20.dp, vertical = 22.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        YuanCoreOrb(
            modifier = Modifier.size(84.dp),
            active = active,
        )
        Spacer(Modifier.width(18.dp))
        Column(modifier = Modifier.weight(1f)) {
            BasicText(
                text = title,
                style = TextStyle(
                    color = Color.White,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.SemiBold,
                    letterSpacing = (-0.2).sp,
                ),
            )
            Spacer(Modifier.height(6.dp))
            BasicText(
                text = subtitle,
                style = TextStyle(
                    color = Color.White.copy(alpha = 0.74f),
                    fontSize = 12.sp,
                    fontFamily = FontFamily.Monospace,
                ),
            )
            Spacer(Modifier.height(14.dp))
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(999.dp))
                    .background(Color.White.copy(alpha = 0.16f))
                    .padding(horizontal = 12.dp, vertical = 6.dp),
            ) {
                BasicText(
                    text = badge,
                    style = TextStyle(
                        color = if (active) YuanCorePalette.Teal else YuanCorePalette.Amber,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Medium,
                    ),
                )
            }
        }
    }
}
