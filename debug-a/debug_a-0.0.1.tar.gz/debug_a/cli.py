# -*- coding: utf-8 -*-
import click

@click.group("da", invoke_without_command=True)
@click.pass_context
def debug_a(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("A股盯盘机器人 \n  请执行 debug_a --help 查看帮助！")


@debug_a.command("psc")
@click.option("-c", "--code", type=str, prompt=True, help="单只股票代码，如：'600122'")
@click.option("-l", "--low", type=float, prompt=True, help="最低价格")
@click.option("-h", "--high", type=float, prompt=True, help='最高价格')
def sm_price_section_monitor(code, low, high):
    """sm_price_section_monitor | 监控单只股票的价格区间"""
    from debug_a.monitor.single_monitor import price_section_monitor
    price_section_monitor(str(code), float(low), float(high), max_nums=3)
    # 问题：命令行无法停止price_section_monitor，因为它是个死循环

@debug_a.command("env")
def env_status():
    """env_status | 获取当前的市场涨跌情况"""
    from debug_a.monitor.env_monitor import get_env_status
    get_env_status()


if __name__ == "__main__":
    debug_a()


