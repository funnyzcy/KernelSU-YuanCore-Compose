package me.weishu.kernelsu.ui.theme.yuancore

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate

/**
 * The breathing concentric "Yuan Core": the rotating flow arc stands for the
 * ksud daemon, the inner glow for kernel space, and the teal dot for a trusted
 * manager. Pure Canvas, so it works under both the Material and Miuix shells.
 */
@Composable
fun YuanCoreOrb(
    modifier: Modifier = Modifier,
    active: Boolean = true,
    animate: Boolean = true,
) {
    val motion = animate && LocalYuanCoreMotion.current
    val transition = rememberInfiniteTransition(label = "YuanCore")
    val spin by transition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            tween(YuanCoreMotion.SPIN_MS, easing = LinearEasing),
        ),
        label = "YuanCoreSpin",
    )
    val breath by transition.animateFloat(
        initialValue = 0.88f,
        targetValue = 1.06f,
        animationSpec = infiniteRepeatable(
            tween(YuanCoreMotion.BREATH_MS, easing = FastOutSlowInEasing),
            RepeatMode.Reverse,
        ),
        label = "YuanCoreBreath",
    )

    val flow = if (active) YuanCorePalette.Flow
    else listOf(YuanCorePalette.Amber, Color(0xFF9A7440), YuanCorePalette.Rose)

    Canvas(modifier = modifier) {
        val r = size.minDimension / 2f
        val c = Offset(size.width / 2f, size.height / 2f)
        val scale = if (motion) breath else 1f
        val outer = r * 0.80f
        val arcSize = Size(outer * 2f, outer * 2f)
        val arcTopLeft = Offset(c.x - outer, c.y - outer)

        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(flow[0].copy(alpha = 0.34f), Color.Transparent),
                center = c,
                radius = r * 1.06f * scale,
            ),
            radius = r * 1.06f * scale,
            center = c,
        )

        rotate(degrees = if (motion) spin else 0f, pivot = c) {
            drawArc(
                brush = Brush.sweepGradient(
                    colors = flow + listOf(flow[0]),
                    center = c,
                ),
                startAngle = -90f,
                sweepAngle = 286f,
                useCenter = false,
                topLeft = arcTopLeft,
                size = arcSize,
                style = Stroke(
                    width = (r * 0.10f).coerceAtLeast(2f),
                    cap = StrokeCap.Round,
                ),
            )
        }

        drawCircle(
            color = Color.White.copy(alpha = 0.22f),
            radius = r * 0.58f,
            center = c,
            style = Stroke(width = (r * 0.035f).coerceAtLeast(1f)),
        )

        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(
                    Color.White.copy(alpha = 0.94f),
                    flow[1].copy(alpha = 0.82f),
                    Color.Transparent,
                ),
                center = c,
                radius = r * 0.42f * scale,
            ),
            radius = r * 0.42f * scale,
            center = c,
        )
        drawCircle(color = Color.White, radius = r * 0.13f, center = c)

        if (active) {
            drawCircle(
                color = YuanCorePalette.Teal,
                radius = r * 0.075f,
                center = Offset(c.x + r * 0.74f, c.y - r * 0.60f),
            )
        }
    }
}
