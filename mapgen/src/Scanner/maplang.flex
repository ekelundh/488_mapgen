/*
 * Seung Hyun Kim
 * Henry Ekelund
 */

/* Mapgen language lexer specification */

package Scanner;

import java_cup.runtime.*;
import java_cup.runtime.ComplexSymbolFactory;
import java_cup.runtime.ComplexSymbolFactory.Location;
import Parser.sym;

%%

%public
%class Scanner
%implements Parser.sym


%line
%column

%cup
%cupdebug

%{
    StringBuffer string = new StringBuffer();
    ComplexSymbolFactory symbolFactory;
    public Scanner(java.io.Reader in, ComplexSymbolFactory sf){
        this(in);
        symbolFactory = sf;
    }

    private Symbol symbol(String name, int sym) {
        return symbolFactory.newSymbol(name, sym, new Location(yyline+1,yycolumn+1,yychar),
        new Location(yyline+1,yycolumn+yylength(),yychar+yylength()));
    }

    private Symbol symbol(String name, int sym, Object val) {
        Location left = new Location(yyline+1,yycolumn+1,yychar);
        Location right= new Location(yyline+1,yycolumn+yylength(), yychar+yylength());
        return symbolFactory.newSymbol(name, sym, left, right,val);
    }
    private Symbol symbol(String name, int sym, Object val,int buflength) {
        Location left = new Location(yyline+1,yycolumn+yylength()-buflength,yychar+yylength()-buflength);
        Location right= new Location(yyline+1,yycolumn+yylength(), yychar+yylength());
        return symbolFactory.newSymbol(name, sym, left, right,val);
    }
        private void error(String message) {
        System.out.println("Error at line "+(yyline+1)+", column "+(yycolumn+1)+" : "+message);
    }
%}

/* main character classes */
LineTerminator = \r|\n|\r\n
InputCharacter = [^\r\n]

WhiteSpace = {LineTerminator} | [ \t\f]

/* comments */
Comment = {TraditionalComment} | {EndOfLineComment} | {DocumentationComment}

TraditionalComment = "/*" [^*] ~"*/" | "/*" "*"+ "/"
EndOfLineComment = "//" {InputCharacter}* {LineTerminator}?
DocumentationComment = "/*" "*"+ [^/*] ~"*/"

/* identifiers */
Identifier = [:jletter:][:jletterdigit:]*

/* integer literals */
DecIntegerLiteral = 0 | [1-9][0-9]*

/* character literals */
SingleCharacter = [^\r\n\'\\]

%state CHARLITERAL

%%

<YYINITIAL> {

  /* keywords */
  "boolean"                      { return symbol("boolean", BOOLEAN); }
  "break"                        { return symbol("break", BREAK); }
  "actor"                        { return symbol("actor", ACTOR); }
  "else"                         { return symbol("else", ELSE); }
  "int"                          { return symbol("int", INT); }
  "map"                          { return symbol("map", MAP); }
  "if"                           { return symbol("if", IF); }
  "return"                       { return symbol("return", RETURN); }
  "void"                         { return symbol("void", VOID); }
  "while"                        { return symbol("while", WHILE); }

  "Actors"                       { return symbol("actorsdecl", ACTORSDECL); }
  "MapOptions"                   { return symbol("mapoptions", MAPOPTIONSDECL); }
  "generator"                    { return symbol("generator", GENERATOR); }
  
  /* boolean literals */
  "true"                         { return symbol("true", BOOLEAN_LITERAL, true); }
  "false"                        { return symbol("false", BOOLEAN_LITERAL, false); }

  
  
  /* separators */
  "("                            { return symbol("lparen", LPAREN); }
  ")"                            { return symbol("rparen", RPAREN); }
  "{"                            { return symbol("lbrace", LBRACE); }
  "}"                            { return symbol("rbrace", RBRACE); }
  "["                            { return symbol("lbrack", LBRACK); }
  "]"                            { return symbol("rbrack", RBRACK); }
  ":"                            { return symbol("colon", COLON); }
  ";"                            { return symbol("semicolon", SEMICOLON); }
  ","                            { return symbol("comma", COMMA); }
  "."                            { return symbol("dot", DOT); }

  /* operators */
  "="                            { return symbol("eq", EQ); }
  ">"                            { return symbol("gt", GT); }
  "<"                            { return symbol("lt", LT); }
  "!"                            { return symbol("not", NOT); }
  "=="                           { return symbol("eqeq", EQEQ); }
  "<="                           { return symbol("ltea", LTEQ); }
  ">="                           { return symbol("gteq", GTEQ); }
  "!="                           { return symbol("noteq", NOTEQ); }
  "&&"                           { return symbol("andand", ANDAND); }
  "||"                           { return symbol("oror", OROR); }
  "+"                            { return symbol("plus", PLUS); }
  "-"                            { return symbol("minus", MINUS); }
  "*"                            { return symbol("mult", MULT); }
  "/"                            { return symbol("div", DIV); }
  "%"                            { return symbol("mod", MOD); }
  "*="                           { return symbol("multeq", MULTEQ); }
  "/="                           { return symbol("diveq", DIVEQ); }
  "%="                           { return symbol("modeq", MODEQ); }
  "+="                           { return symbol("pluseq", PLUSEQ); }
  "-="                           { return symbol("minuseq", MINUSEQ); }

  /* character literal */
  \'                             { yybegin(CHARLITERAL); }

  /* numeric literals */

  /* This is matched together with the minus, because the number is too big to
     be represented by a positive integer. */
  "-2147483648"                  { return symbol("intlit", INTEGER_LITERAL, new Integer(Integer.MIN_VALUE)); }

  {DecIntegerLiteral}            { return symbol("intlit", INTEGER_LITERAL, new Integer(yytext())); }

  /* comments */
  {Comment}                      { /* ignore */ }

  /* whitespace */
  {WhiteSpace}                   { /* ignore */ }

  /* identifiers */
  {Identifier}                   { return symbol("identifier", IDENTIFIER, yytext()); }
}

<CHARLITERAL> {
  {SingleCharacter}\'            { yybegin(YYINITIAL); return symbol("charlit", CHARACTER_LITERAL, yytext().charAt(0)); }

  /* escape sequences */
  "\\b"\'                        { yybegin(YYINITIAL); return symbol("backspace", CHARACTER_LITERAL, '\b');}
  "\\t"\'                        { yybegin(YYINITIAL); return symbol("tab", CHARACTER_LITERAL, '\t');}
  "\\n"\'                        { yybegin(YYINITIAL); return symbol("newline", CHARACTER_LITERAL, '\n');}
  "\\f"\'                        { yybegin(YYINITIAL); return symbol("formfeed", CHARACTER_LITERAL, '\f');}
  "\\r"\'                        { yybegin(YYINITIAL); return symbol("carriagereturn", CHARACTER_LITERAL, '\r');}
  "\\\""\'                       { yybegin(YYINITIAL); return symbol("doublequote", CHARACTER_LITERAL, '\"');}
  "\\'"\'                        { yybegin(YYINITIAL); return symbol("singlequote", CHARACTER_LITERAL, '\'');}
  "\\\\"\'                       { yybegin(YYINITIAL); return symbol("backslash", CHARACTER_LITERAL, '\\'); }

  /* error cases */
  \\.                            { throw new RuntimeException("Illegal escape sequence \""+yytext()+"\""); }
  {LineTerminator}               { throw new RuntimeException("Unterminated character literal at end of line"); }
}

/* error fallback */
[^]                              { throw new RuntimeException("Illegal character \""+yytext()+
                                                              "\" at line "+yyline+", column "+yycolumn); }
<<EOF>>                          { return symbol("", EOF); }