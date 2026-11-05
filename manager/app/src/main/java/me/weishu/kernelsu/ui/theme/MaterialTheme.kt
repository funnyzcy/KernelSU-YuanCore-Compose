package me.weishu.kernelsu.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialExpressiveTheme
import androidx.compose.material3.MotionScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.core.view.WindowInsetsControllerCompat
import me.weishu.kernelsu.ui.webui.MonetColorsProvider
import me.weishu.kernelsu.ui.theme.yuancore.YuanCorePalette
import me.weishu.kernelsu.ui.theme.yuancore.YuanCoreShapes
import me.weishu.kernelsu.ui.theme.yuancore.yuanCore
import me.weishu.kernelsu.ui.theme.yuancore.yuanCoreType

@Composable
fun MaterialKernelSUTheme(
    appSettings: AppSettings,
    content: @Composable () -> Unit
) {
    val context = LocalContext.current
    val systemDarkTheme = isSystemInDarkTheme()
    val darkTheme = appSettings.colorMode.isDark || (appSettings.colorMode.isSystem && systemDarkTheme)
    val amoledMode = appSettings.colorMode.isAmoled
    val dynamicColor = appSettings.keyColor == 0

    val yuanCore = appSettings.yuanCoreEnabled
    val colorScheme = rememberKernelSUColorScheme(
        seedColor = when {
            yuanCore -> YuanCorePalette.Seed
            dynamicColor -> Color.Unspecified
            else -> Color(appSettings.keyColor)
        },
        isDark = darkTheme,
        isAmoled = amoledMode,
        paletteStyle = appSettings.paletteStyle,
        colorSpec = appSettings.colorSpec,
    ).let { if (yuanCore) it.yuanCore(darkTheme, amoledMode) else it }

    LaunchedEffect(darkTheme) {
        val window = (context as? Activity)?.window ?: return@LaunchedEffect
        WindowInsetsControllerCompat(window, window.decorView).apply {
            isAppearanceLightStatusBars = !darkTheme
            isAppearanceLightNavigationBars = !darkTheme
        }
    }

    val animatedColorScheme = colorScheme.animateAsState()

    MaterialExpressiveTheme(
        colorScheme = animatedColorScheme,
        motionScheme = MotionScheme.expressive(),
        shapes = if (yuanCore) YuanCoreShapes else null,
        typography = if (yuanCore) Typography.yuanCoreType() else Typography,
        content = {
            MonetColorsProvider.UpdateCss(colorScheme)
            content()
        }
    )
}
