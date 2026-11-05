package me.weishu.kernelsu.ui.theme.yuancore

import androidx.compose.material3.Typography
import androidx.compose.runtime.staticCompositionLocalOf

/**
 * Whether the YuanCore theme is enabled. Provided once by KernelSUTheme, read
 * by screens that want to opt into YuanCore-only composables (e.g. the hero
 * card). Defaults to false so unrelated hosts keep the upstream appearance.
 */
val LocalYuanCoreEnabled = staticCompositionLocalOf { false }

/** Set to false to freeze the orb animation (reduced motion, screenshot tests). */
val LocalYuanCoreMotion = staticCompositionLocalOf { true }

/**
 * Apply YuanCore's numeric typography to label/body styles most likely to carry
 * versions, counts and kernel versions. Merging only the numeric face keeps
 * every upstream size and weight intact.
 */
fun Typography.yuanCoreType(): Typography = copy(
    labelLarge = labelLarge.merge(YuanCoreNumeric),
    labelMedium = labelMedium.merge(YuanCoreNumeric),
    labelSmall = labelSmall.merge(YuanCoreNumeric),
    bodySmall = bodySmall.merge(YuanCoreNumeric),
)
