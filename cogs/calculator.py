"""File for the Calculator cog"""
from __future__ import division

import asyncio
import math
import operator
import random

import discord
from discord.ext import commands
from pyparsing import (CaselessLiteral, Combine, Forward, Group, Literal,
                       Optional, Word, ZeroOrMore, alphas, nums, oneOf)


class NumericStringParser(object):
    """
    Most of this code comes from the fourFn.py example in pyparsing github repository
    """

    def pushFirst(self, strg, loc, toks):
        self.exprStack.append(toks[0])

    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == "-":
            self.exprStack.append("unary -")

    def __init__(self):
        """
        expop   :: '^'
        multop  :: 'x' | '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(
            Word("+-" + nums, nums)
            + Optional(point + Optional(Word(nums)))
            + Optional(e + Word("+-" + nums, nums))
        )
        ident = Word(alphas, alphas + nums + "_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("x")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        add_operators = plus | minus
        multiply_operators = mult | div
        exponent_operators = Literal("^")
        pi = CaselessLiteral("PI")
        expr = Forward()
        atom = (
            (
                Optional(oneOf("- +"))
                + (pi | e | fnumber | ident + lpar + expr + rpar).setParseAction(
                    self.pushFirst
                )
            )
            | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
        ).setParseAction(self.pushUMinus)
        # by defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + ZeroOrMore(
            (exponent_operators + factor).setParseAction(self.pushFirst)
        )
        term = factor + ZeroOrMore(
            (multiply_operators + factor).setParseAction(self.pushFirst)
        )
        expr << term + ZeroOrMore((add_operators + term).setParseAction(self.pushFirst))
        # addop_term = ( addop + term ).setParseAction( self.pushFirst )
        # general_term = term + ZeroOrMore( addop_term ) | OneOrMore( addop_term)
        # expr <<  general_term
        self.bnf = expr
        # map operator symbols to corresponding arithmetic operations
        self.operators = {
            "+": operator.add,
            "-": operator.sub,
            "x": operator.mul,
            "/": operator.truediv,
            "^": operator.pow,
            "**": operator.pow,
        }
        self.functions = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "abs": abs,
            "trunc": lambda a: int(a),
            "round": round,
            "floor": math.floor,
            "ceil": math.ceil,
        }

    def evaluateStack(self, stack):
        operator = stack.pop()
        if operator == "unary -":
            return -self.evaluateStack(stack)
        if operator in "+-x/^":
            op2 = self.evaluateStack(stack)
            op1 = self.evaluateStack(stack)
            return self.operators[operator](op1, op2)
        elif operator == "PI":
            return math.pi  # 3.1415926535
        elif operator == "E":
            return math.e  # 2.718281828
        elif operator in self.functions:
            return self.functions[operator](self.evaluateStack(stack))
        elif operator[0].isalpha():
            return 0
        else:
            return float(operator)

    def eval(self, num_string, parse_all=True):
        self.expression_stack = []
        val = self.evaluateStack(self.expression_stack[:])
        return val


class Calculator(commands.Cog):
    """Calculator calculates stuff (math)"""

    # Init with the bot reference, and a reference to the settings var
    def __init__(self, bot):
        self.bot = bot
        self.nsp = NumericStringParser()

    @commands.command(aliases=["math", "calculator", "calculate"])
    async def calc(self, ctx, *, formula):
        """This command basically does math for you

        Parameters
        ----------
        formula : string, optional
            the math formula to be evaluated

        Returns
        -------
        string
            the formula used and it's answer
        """

        formula = formula.replace("*", "x")

        try:
            answer = self.nsp.eval(formula)
        except:
            msg = 'I couldn\'t calculate "{}" :(\n\n'.format(
                formula.replace("*", "\\*").replace("`", "\\`").replace("_", "\\_")
            )
            return await ctx.send(msg)

        if int(answer) == answer:
            # Check if it's a whole number and cast to int if so
            answer = int(answer)

        # Say message
        await ctx.send("{} = {}".format(formula, answer))


def setup(bot):
    """Adds the cog to the bot"""
    # Add the bot
    bot.add_cog(Calculator(bot))
