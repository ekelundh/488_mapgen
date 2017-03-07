import Parser.Parser;
import Scanner.Scanner;
import java_cup.runtime.ComplexSymbolFactory;

import java_cup.runtime.ScannerBuffer;
import java_cup.runtime.XMLElement;

import javax.xml.stream.XMLOutputFactory;
import javax.xml.stream.XMLStreamWriter;
import java.io.*;

import javax.xml.transform.*;
import javax.xml.transform.stream.*;
import java.io.FileReader;

public class Main {
    private static String TREE_XSL = "tree.xsl";
    private static String TREE_VIEW_XSL = "tree-view.xsl";
    private static String INTERMEDIATE_OUTPUT = "tempOut.xml";

    public static void main(String[] args) throws Exception {
        String input = args[0];

        String outputSuffix = input.substring(0, input.lastIndexOf('.'));
        String outputXml = outputSuffix + ".xml";
        String outputHtml = outputSuffix + ".html";

        // initialize the symbol factory
        ComplexSymbolFactory csf = new ComplexSymbolFactory();
        // create a buffering scanner wrapper

        ScannerBuffer lexer = new ScannerBuffer(new Scanner(new BufferedReader(new FileReader(input)), csf));
        // start parsing
        Parser p = new Parser(lexer, csf);
        XMLElement e = (XMLElement) p.parse().value;
        // create XML output file
        XMLOutputFactory outFactory = XMLOutputFactory.newInstance();
        XMLStreamWriter sw = outFactory.createXMLStreamWriter(new FileOutputStream(INTERMEDIATE_OUTPUT), "UTF-8");
        // dump XML output to the file
        XMLElement.dump(lexer, sw, e);

        // transform the parse tree into an AST and a rendered HTML version
        Transformer transformer = TransformerFactory.newInstance()
                .newTransformer(new StreamSource(new File(TREE_XSL)));
        Source text = new StreamSource(new File(INTERMEDIATE_OUTPUT));
        transformer.transform(text, new StreamResult(new File(outputXml)));
        transformer = TransformerFactory.newInstance()
                .newTransformer(new StreamSource(new File(TREE_VIEW_XSL)));
        text = new StreamSource(new File(outputXml));
        transformer.transform(text, new StreamResult(new File(outputHtml)));
    }
}
