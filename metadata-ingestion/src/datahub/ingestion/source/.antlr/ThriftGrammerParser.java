// Generated from /home/waylee/datahub/metadata-ingestion/src/datahub/ingestion/source/ThriftGrammer.g4 by ANTLR 4.8
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast"})
public class ThriftGrammerParser extends Parser {
	static { RuntimeMetaData.checkVersion("4.8", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		T__0=1, T__1=2, T__2=3, T__3=4, T__4=5, T__5=6, T__6=7, T__7=8, T__8=9, 
		T__9=10, T__10=11, T__11=12, T__12=13, T__13=14, T__14=15, T__15=16, T__16=17, 
		T__17=18, T__18=19, T__19=20, T__20=21, T__21=22, T__22=23, T__23=24, 
		T__24=25, T__25=26, T__26=27, T__27=28, T__28=29, T__29=30, T__30=31, 
		T__31=32, T__32=33, T__33=34, T__34=35, T__35=36, INTEGER=37, HEX_INTEGER=38, 
		DOUBLE=39, TYPE_BOOL=40, TYPE_BYTE=41, TYPE_I16=42, TYPE_I32=43, TYPE_I64=44, 
		TYPE_DOUBLE=45, TYPE_STRING=46, TYPE_BINARY=47, LITERAL=48, IDENTIFIER=49, 
		COMMA=50, WS=51, SL_COMMENT=52, ML_COMMENT=53;
	public static final int
		RULE_document = 0, RULE_header = 1, RULE_include_ = 2, RULE_namespace_ = 3, 
		RULE_cpp_include = 4, RULE_definition = 5, RULE_const_rule = 6, RULE_typedef_ = 7, 
		RULE_enum_rule = 8, RULE_enum_field = 9, RULE_senum = 10, RULE_struct_ = 11, 
		RULE_union_ = 12, RULE_exception = 13, RULE_service = 14, RULE_field = 15, 
		RULE_field_id = 16, RULE_field_req = 17, RULE_function_ = 18, RULE_oneway = 19, 
		RULE_function_type = 20, RULE_throws_list = 21, RULE_type_annotations = 22, 
		RULE_type_annotation = 23, RULE_annotation_value = 24, RULE_field_type = 25, 
		RULE_base_type = 26, RULE_container_type = 27, RULE_map_type = 28, RULE_set_type = 29, 
		RULE_list_type = 30, RULE_cpp_type = 31, RULE_const_value = 32, RULE_integer = 33, 
		RULE_const_list = 34, RULE_const_map_entry = 35, RULE_const_map = 36, 
		RULE_list_separator = 37, RULE_real_base_type = 38;
	private static String[] makeRuleNames() {
		return new String[] {
			"document", "header", "include_", "namespace_", "cpp_include", "definition", 
			"const_rule", "typedef_", "enum_rule", "enum_field", "senum", "struct_", 
			"union_", "exception", "service", "field", "field_id", "field_req", "function_", 
			"oneway", "function_type", "throws_list", "type_annotations", "type_annotation", 
			"annotation_value", "field_type", "base_type", "container_type", "map_type", 
			"set_type", "list_type", "cpp_type", "const_value", "integer", "const_list", 
			"const_map_entry", "const_map", "list_separator", "real_base_type"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'include'", "'namespace'", "'*'", "'cpp_namespace'", "'php_namespace'", 
			"'cpp_include'", "'const'", "'='", "'typedef'", "'enum'", "'{'", "'}'", 
			"'senum'", "'struct'", "'union'", "'exception'", "'service'", "'extends'", 
			"':'", "'required'", "'optional'", "'('", "')'", "'oneway'", "'async'", 
			"'void'", "'throws'", "'map'", "'<'", "'>'", "'set'", "'list'", "'cpp_type'", 
			"'['", "']'", "';'", null, null, null, "'bool'", "'byte'", "'i16'", "'i32'", 
			"'i64'", "'double'", "'string'", "'binary'", null, null, "','"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, "INTEGER", "HEX_INTEGER", "DOUBLE", "TYPE_BOOL", "TYPE_BYTE", "TYPE_I16", 
			"TYPE_I32", "TYPE_I64", "TYPE_DOUBLE", "TYPE_STRING", "TYPE_BINARY", 
			"LITERAL", "IDENTIFIER", "COMMA", "WS", "SL_COMMENT", "ML_COMMENT"
		};
	}
	private static final String[] _SYMBOLIC_NAMES = makeSymbolicNames();
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}

	@Override
	public String getGrammarFileName() { return "ThriftGrammer.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public ThriftGrammerParser(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	public static class DocumentContext extends ParserRuleContext {
		public TerminalNode EOF() { return getToken(ThriftGrammerParser.EOF, 0); }
		public List<HeaderContext> header() {
			return getRuleContexts(HeaderContext.class);
		}
		public HeaderContext header(int i) {
			return getRuleContext(HeaderContext.class,i);
		}
		public List<DefinitionContext> definition() {
			return getRuleContexts(DefinitionContext.class);
		}
		public DefinitionContext definition(int i) {
			return getRuleContext(DefinitionContext.class,i);
		}
		public DocumentContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_document; }
	}

	public final DocumentContext document() throws RecognitionException {
		DocumentContext _localctx = new DocumentContext(_ctx, getState());
		enterRule(_localctx, 0, RULE_document);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(81);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__0) | (1L << T__1) | (1L << T__3) | (1L << T__4) | (1L << T__5))) != 0)) {
				{
				{
				setState(78);
				header();
				}
				}
				setState(83);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(87);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__6) | (1L << T__8) | (1L << T__9) | (1L << T__12) | (1L << T__13) | (1L << T__14) | (1L << T__15) | (1L << T__16))) != 0)) {
				{
				{
				setState(84);
				definition();
				}
				}
				setState(89);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(90);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class HeaderContext extends ParserRuleContext {
		public Include_Context include_() {
			return getRuleContext(Include_Context.class,0);
		}
		public Namespace_Context namespace_() {
			return getRuleContext(Namespace_Context.class,0);
		}
		public Cpp_includeContext cpp_include() {
			return getRuleContext(Cpp_includeContext.class,0);
		}
		public HeaderContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_header; }
	}

	public final HeaderContext header() throws RecognitionException {
		HeaderContext _localctx = new HeaderContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_header);
		try {
			setState(95);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__0:
				enterOuterAlt(_localctx, 1);
				{
				setState(92);
				include_();
				}
				break;
			case T__1:
			case T__3:
			case T__4:
				enterOuterAlt(_localctx, 2);
				{
				setState(93);
				namespace_();
				}
				break;
			case T__5:
				enterOuterAlt(_localctx, 3);
				{
				setState(94);
				cpp_include();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Include_Context extends ParserRuleContext {
		public TerminalNode LITERAL() { return getToken(ThriftGrammerParser.LITERAL, 0); }
		public Include_Context(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_include_; }
	}

	public final Include_Context include_() throws RecognitionException {
		Include_Context _localctx = new Include_Context(_ctx, getState());
		enterRule(_localctx, 4, RULE_include_);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(97);
			match(T__0);
			setState(98);
			match(LITERAL);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Namespace_Context extends ParserRuleContext {
		public List<TerminalNode> IDENTIFIER() { return getTokens(ThriftGrammerParser.IDENTIFIER); }
		public TerminalNode IDENTIFIER(int i) {
			return getToken(ThriftGrammerParser.IDENTIFIER, i);
		}
		public TerminalNode LITERAL() { return getToken(ThriftGrammerParser.LITERAL, 0); }
		public Namespace_Context(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_namespace_; }
	}

	public final Namespace_Context namespace_() throws RecognitionException {
		Namespace_Context _localctx = new Namespace_Context(_ctx, getState());
		enterRule(_localctx, 6, RULE_namespace_);
		int _la;
		try {
			setState(110);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,3,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(100);
				match(T__1);
				setState(101);
				match(T__2);
				setState(102);
				_la = _input.LA(1);
				if ( !(_la==LITERAL || _la==IDENTIFIER) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(103);
				match(T__1);
				setState(104);
				match(IDENTIFIER);
				setState(105);
				_la = _input.LA(1);
				if ( !(_la==LITERAL || _la==IDENTIFIER) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
				break;
			case 3:
				enterOuterAlt(_localctx, 3);
				{
				setState(106);
				match(T__3);
				setState(107);
				match(IDENTIFIER);
				}
				break;
			case 4:
				enterOuterAlt(_localctx, 4);
				{
				setState(108);
				match(T__4);
				setState(109);
				match(IDENTIFIER);
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Cpp_includeContext extends ParserRuleContext {
		public TerminalNode LITERAL() { return getToken(ThriftGrammerParser.LITERAL, 0); }
		public Cpp_includeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_cpp_include; }
	}

	public final Cpp_includeContext cpp_include() throws RecognitionException {
		Cpp_includeContext _localctx = new Cpp_includeContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_cpp_include);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(112);
			match(T__5);
			setState(113);
			match(LITERAL);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class DefinitionContext extends ParserRuleContext {
		public Const_ruleContext const_rule() {
			return getRuleContext(Const_ruleContext.class,0);
		}
		public Typedef_Context typedef_() {
			return getRuleContext(Typedef_Context.class,0);
		}
		public Enum_ruleContext enum_rule() {
			return getRuleContext(Enum_ruleContext.class,0);
		}
		public SenumContext senum() {
			return getRuleContext(SenumContext.class,0);
		}
		public Struct_Context struct_() {
			return getRuleContext(Struct_Context.class,0);
		}
		public Union_Context union_() {
			return getRuleContext(Union_Context.class,0);
		}
		public ExceptionContext exception() {
			return getRuleContext(ExceptionContext.class,0);
		}
		public ServiceContext service() {
			return getRuleContext(ServiceContext.class,0);
		}
		public DefinitionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_definition; }
	}

	public final DefinitionContext definition() throws RecognitionException {
		DefinitionContext _localctx = new DefinitionContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_definition);
		try {
			setState(123);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__6:
				enterOuterAlt(_localctx, 1);
				{
				setState(115);
				const_rule();
				}
				break;
			case T__8:
				enterOuterAlt(_localctx, 2);
				{
				setState(116);
				typedef_();
				}
				break;
			case T__9:
				enterOuterAlt(_localctx, 3);
				{
				setState(117);
				enum_rule();
				}
				break;
			case T__12:
				enterOuterAlt(_localctx, 4);
				{
				setState(118);
				senum();
				}
				break;
			case T__13:
				enterOuterAlt(_localctx, 5);
				{
				setState(119);
				struct_();
				}
				break;
			case T__14:
				enterOuterAlt(_localctx, 6);
				{
				setState(120);
				union_();
				}
				break;
			case T__15:
				enterOuterAlt(_localctx, 7);
				{
				setState(121);
				exception();
				}
				break;
			case T__16:
				enterOuterAlt(_localctx, 8);
				{
				setState(122);
				service();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Const_ruleContext extends ParserRuleContext {
		public Field_typeContext field_type() {
			return getRuleContext(Field_typeContext.class,0);
		}
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public Const_valueContext const_value() {
			return getRuleContext(Const_valueContext.class,0);
		}
		public List_separatorContext list_separator() {
			return getRuleContext(List_separatorContext.class,0);
		}
		public Const_ruleContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_const_rule; }
	}

	public final Const_ruleContext const_rule() throws RecognitionException {
		Const_ruleContext _localctx = new Const_ruleContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_const_rule);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(125);
			match(T__6);
			setState(126);
			field_type();
			setState(127);
			match(IDENTIFIER);
			setState(130);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__7) {
				{
				setState(128);
				match(T__7);
				setState(129);
				const_value();
				}
			}

			setState(133);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__35 || _la==COMMA) {
				{
				setState(132);
				list_separator();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Typedef_Context extends ParserRuleContext {
		public Field_typeContext field_type() {
			return getRuleContext(Field_typeContext.class,0);
		}
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public Type_annotationsContext type_annotations() {
			return getRuleContext(Type_annotationsContext.class,0);
		}
		public Typedef_Context(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_typedef_; }
	}

	public final Typedef_Context typedef_() throws RecognitionException {
		Typedef_Context _localctx = new Typedef_Context(_ctx, getState());
		enterRule(_localctx, 14, RULE_typedef_);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(135);
			match(T__8);
			setState(136);
			field_type();
			setState(137);
			match(IDENTIFIER);
			setState(139);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__21) {
				{
				setState(138);
				type_annotations();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Enum_ruleContext extends ParserRuleContext {
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public List<Enum_fieldContext> enum_field() {
			return getRuleContexts(Enum_fieldContext.class);
		}
		public Enum_fieldContext enum_field(int i) {
			return getRuleContext(Enum_fieldContext.class,i);
		}
		public Type_annotationsContext type_annotations() {
			return getRuleContext(Type_annotationsContext.class,0);
		}
		public Enum_ruleContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_enum_rule; }
	}

	public final Enum_ruleContext enum_rule() throws RecognitionException {
		Enum_ruleContext _localctx = new Enum_ruleContext(_ctx, getState());
		enterRule(_localctx, 16, RULE_enum_rule);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(141);
			match(T__9);
			setState(142);
			match(IDENTIFIER);
			setState(143);
			match(T__10);
			setState(147);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==IDENTIFIER) {
				{
				{
				setState(144);
				enum_field();
				}
				}
				setState(149);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(150);
			match(T__11);
			setState(152);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__21) {
				{
				setState(151);
				type_annotations();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Enum_fieldContext extends ParserRuleContext {
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public IntegerContext integer() {
			return getRuleContext(IntegerContext.class,0);
		}
		public Type_annotationsContext type_annotations() {
			return getRuleContext(Type_annotationsContext.class,0);
		}
		public List_separatorContext list_separator() {
			return getRuleContext(List_separatorContext.class,0);
		}
		public Enum_fieldContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_enum_field; }
	}

	public final Enum_fieldContext enum_field() throws RecognitionException {
		Enum_fieldContext _localctx = new Enum_fieldContext(_ctx, getState());
		enterRule(_localctx, 18, RULE_enum_field);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(154);
			match(IDENTIFIER);
			setState(157);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__7) {
				{
				setState(155);
				match(T__7);
				setState(156);
				integer();
				}
			}

			setState(160);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__21) {
				{
				setState(159);
				type_annotations();
				}
			}

			setState(163);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__35 || _la==COMMA) {
				{
				setState(162);
				list_separator();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class SenumContext extends ParserRuleContext {
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public List<TerminalNode> LITERAL() { return getTokens(ThriftGrammerParser.LITERAL); }
		public TerminalNode LITERAL(int i) {
			return getToken(ThriftGrammerParser.LITERAL, i);
		}
		public Type_annotationsContext type_annotations() {
			return getRuleContext(Type_annotationsContext.class,0);
		}
		public List<List_separatorContext> list_separator() {
			return getRuleContexts(List_separatorContext.class);
		}
		public List_separatorContext list_separator(int i) {
			return getRuleContext(List_separatorContext.class,i);
		}
		public SenumContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_senum; }
	}

	public final SenumContext senum() throws RecognitionException {
		SenumContext _localctx = new SenumContext(_ctx, getState());
		enterRule(_localctx, 20, RULE_senum);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(165);
			match(T__12);
			setState(166);
			match(IDENTIFIER);
			setState(167);
			match(T__10);
			setState(174);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==LITERAL) {
				{
				{
				setState(168);
				match(LITERAL);
				setState(170);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==T__35 || _la==COMMA) {
					{
					setState(169);
					list_separator();
					}
				}

				}
				}
				setState(176);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(177);
			match(T__11);
			setState(179);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__21) {
				{
				setState(178);
				type_annotations();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Struct_Context extends ParserRuleContext {
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public List<FieldContext> field() {
			return getRuleContexts(FieldContext.class);
		}
		public FieldContext field(int i) {
			return getRuleContext(FieldContext.class,i);
		}
		public Type_annotationsContext type_annotations() {
			return getRuleContext(Type_annotationsContext.class,0);
		}
		public Struct_Context(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_struct_; }
	}

	public final Struct_Context struct_() throws RecognitionException {
		Struct_Context _localctx = new Struct_Context(_ctx, getState());
		enterRule(_localctx, 22, RULE_struct_);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(181);
			match(T__13);
			setState(182);
			match(IDENTIFIER);
			setState(183);
			match(T__10);
			setState(187);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__19) | (1L << T__20) | (1L << T__27) | (1L << T__30) | (1L << T__31) | (1L << INTEGER) | (1L << HEX_INTEGER) | (1L << TYPE_BOOL) | (1L << TYPE_BYTE) | (1L << TYPE_I16) | (1L << TYPE_I32) | (1L << TYPE_I64) | (1L << TYPE_DOUBLE) | (1L << TYPE_STRING) | (1L << TYPE_BINARY) | (1L << IDENTIFIER))) != 0)) {
				{
				{
				setState(184);
				field();
				}
				}
				setState(189);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(190);
			match(T__11);
			setState(192);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__21) {
				{
				setState(191);
				type_annotations();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Union_Context extends ParserRuleContext {
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public List<FieldContext> field() {
			return getRuleContexts(FieldContext.class);
		}
		public FieldContext field(int i) {
			return getRuleContext(FieldContext.class,i);
		}
		public Type_annotationsContext type_annotations() {
			return getRuleContext(Type_annotationsContext.class,0);
		}
		public Union_Context(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_union_; }
	}

	public final Union_Context union_() throws RecognitionException {
		Union_Context _localctx = new Union_Context(_ctx, getState());
		enterRule(_localctx, 24, RULE_union_);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(194);
			match(T__14);
			setState(195);
			match(IDENTIFIER);
			setState(196);
			match(T__10);
			setState(200);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__19) | (1L << T__20) | (1L << T__27) | (1L << T__30) | (1L << T__31) | (1L << INTEGER) | (1L << HEX_INTEGER) | (1L << TYPE_BOOL) | (1L << TYPE_BYTE) | (1L << TYPE_I16) | (1L << TYPE_I32) | (1L << TYPE_I64) | (1L << TYPE_DOUBLE) | (1L << TYPE_STRING) | (1L << TYPE_BINARY) | (1L << IDENTIFIER))) != 0)) {
				{
				{
				setState(197);
				field();
				}
				}
				setState(202);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(203);
			match(T__11);
			setState(205);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__21) {
				{
				setState(204);
				type_annotations();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ExceptionContext extends ParserRuleContext {
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public List<FieldContext> field() {
			return getRuleContexts(FieldContext.class);
		}
		public FieldContext field(int i) {
			return getRuleContext(FieldContext.class,i);
		}
		public Type_annotationsContext type_annotations() {
			return getRuleContext(Type_annotationsContext.class,0);
		}
		public ExceptionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_exception; }
	}

	public final ExceptionContext exception() throws RecognitionException {
		ExceptionContext _localctx = new ExceptionContext(_ctx, getState());
		enterRule(_localctx, 26, RULE_exception);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(207);
			match(T__15);
			setState(208);
			match(IDENTIFIER);
			setState(209);
			match(T__10);
			setState(213);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__19) | (1L << T__20) | (1L << T__27) | (1L << T__30) | (1L << T__31) | (1L << INTEGER) | (1L << HEX_INTEGER) | (1L << TYPE_BOOL) | (1L << TYPE_BYTE) | (1L << TYPE_I16) | (1L << TYPE_I32) | (1L << TYPE_I64) | (1L << TYPE_DOUBLE) | (1L << TYPE_STRING) | (1L << TYPE_BINARY) | (1L << IDENTIFIER))) != 0)) {
				{
				{
				setState(210);
				field();
				}
				}
				setState(215);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(216);
			match(T__11);
			setState(218);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__21) {
				{
				setState(217);
				type_annotations();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ServiceContext extends ParserRuleContext {
		public List<TerminalNode> IDENTIFIER() { return getTokens(ThriftGrammerParser.IDENTIFIER); }
		public TerminalNode IDENTIFIER(int i) {
			return getToken(ThriftGrammerParser.IDENTIFIER, i);
		}
		public List<Function_Context> function_() {
			return getRuleContexts(Function_Context.class);
		}
		public Function_Context function_(int i) {
			return getRuleContext(Function_Context.class,i);
		}
		public Type_annotationsContext type_annotations() {
			return getRuleContext(Type_annotationsContext.class,0);
		}
		public ServiceContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_service; }
	}

	public final ServiceContext service() throws RecognitionException {
		ServiceContext _localctx = new ServiceContext(_ctx, getState());
		enterRule(_localctx, 28, RULE_service);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(220);
			match(T__16);
			setState(221);
			match(IDENTIFIER);
			setState(224);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__17) {
				{
				setState(222);
				match(T__17);
				setState(223);
				match(IDENTIFIER);
				}
			}

			setState(226);
			match(T__10);
			setState(230);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__23) | (1L << T__24) | (1L << T__25) | (1L << T__27) | (1L << T__30) | (1L << T__31) | (1L << TYPE_BOOL) | (1L << TYPE_BYTE) | (1L << TYPE_I16) | (1L << TYPE_I32) | (1L << TYPE_I64) | (1L << TYPE_DOUBLE) | (1L << TYPE_STRING) | (1L << TYPE_BINARY) | (1L << IDENTIFIER))) != 0)) {
				{
				{
				setState(227);
				function_();
				}
				}
				setState(232);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(233);
			match(T__11);
			setState(235);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__21) {
				{
				setState(234);
				type_annotations();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class FieldContext extends ParserRuleContext {
		public Field_typeContext field_type() {
			return getRuleContext(Field_typeContext.class,0);
		}
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public Field_idContext field_id() {
			return getRuleContext(Field_idContext.class,0);
		}
		public Field_reqContext field_req() {
			return getRuleContext(Field_reqContext.class,0);
		}
		public Const_valueContext const_value() {
			return getRuleContext(Const_valueContext.class,0);
		}
		public Type_annotationsContext type_annotations() {
			return getRuleContext(Type_annotationsContext.class,0);
		}
		public List_separatorContext list_separator() {
			return getRuleContext(List_separatorContext.class,0);
		}
		public FieldContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_field; }
	}

	public final FieldContext field() throws RecognitionException {
		FieldContext _localctx = new FieldContext(_ctx, getState());
		enterRule(_localctx, 30, RULE_field);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(238);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==INTEGER || _la==HEX_INTEGER) {
				{
				setState(237);
				field_id();
				}
			}

			setState(241);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__19 || _la==T__20) {
				{
				setState(240);
				field_req();
				}
			}

			setState(243);
			field_type();
			setState(244);
			match(IDENTIFIER);
			setState(247);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__7) {
				{
				setState(245);
				match(T__7);
				setState(246);
				const_value();
				}
			}

			setState(250);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__21) {
				{
				setState(249);
				type_annotations();
				}
			}

			setState(253);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__35 || _la==COMMA) {
				{
				setState(252);
				list_separator();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Field_idContext extends ParserRuleContext {
		public IntegerContext integer() {
			return getRuleContext(IntegerContext.class,0);
		}
		public Field_idContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_field_id; }
	}

	public final Field_idContext field_id() throws RecognitionException {
		Field_idContext _localctx = new Field_idContext(_ctx, getState());
		enterRule(_localctx, 32, RULE_field_id);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(255);
			integer();
			setState(256);
			match(T__18);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Field_reqContext extends ParserRuleContext {
		public Field_reqContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_field_req; }
	}

	public final Field_reqContext field_req() throws RecognitionException {
		Field_reqContext _localctx = new Field_reqContext(_ctx, getState());
		enterRule(_localctx, 34, RULE_field_req);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(258);
			_la = _input.LA(1);
			if ( !(_la==T__19 || _la==T__20) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Function_Context extends ParserRuleContext {
		public Function_typeContext function_type() {
			return getRuleContext(Function_typeContext.class,0);
		}
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public OnewayContext oneway() {
			return getRuleContext(OnewayContext.class,0);
		}
		public List<FieldContext> field() {
			return getRuleContexts(FieldContext.class);
		}
		public FieldContext field(int i) {
			return getRuleContext(FieldContext.class,i);
		}
		public Throws_listContext throws_list() {
			return getRuleContext(Throws_listContext.class,0);
		}
		public Type_annotationsContext type_annotations() {
			return getRuleContext(Type_annotationsContext.class,0);
		}
		public List_separatorContext list_separator() {
			return getRuleContext(List_separatorContext.class,0);
		}
		public Function_Context(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_function_; }
	}

	public final Function_Context function_() throws RecognitionException {
		Function_Context _localctx = new Function_Context(_ctx, getState());
		enterRule(_localctx, 36, RULE_function_);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(261);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__23 || _la==T__24) {
				{
				setState(260);
				oneway();
				}
			}

			setState(263);
			function_type();
			setState(264);
			match(IDENTIFIER);
			setState(265);
			match(T__21);
			setState(269);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__19) | (1L << T__20) | (1L << T__27) | (1L << T__30) | (1L << T__31) | (1L << INTEGER) | (1L << HEX_INTEGER) | (1L << TYPE_BOOL) | (1L << TYPE_BYTE) | (1L << TYPE_I16) | (1L << TYPE_I32) | (1L << TYPE_I64) | (1L << TYPE_DOUBLE) | (1L << TYPE_STRING) | (1L << TYPE_BINARY) | (1L << IDENTIFIER))) != 0)) {
				{
				{
				setState(266);
				field();
				}
				}
				setState(271);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(272);
			match(T__22);
			setState(274);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__26) {
				{
				setState(273);
				throws_list();
				}
			}

			setState(277);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__21) {
				{
				setState(276);
				type_annotations();
				}
			}

			setState(280);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__35 || _la==COMMA) {
				{
				setState(279);
				list_separator();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class OnewayContext extends ParserRuleContext {
		public OnewayContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_oneway; }
	}

	public final OnewayContext oneway() throws RecognitionException {
		OnewayContext _localctx = new OnewayContext(_ctx, getState());
		enterRule(_localctx, 38, RULE_oneway);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(282);
			_la = _input.LA(1);
			if ( !(_la==T__23 || _la==T__24) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Function_typeContext extends ParserRuleContext {
		public Field_typeContext field_type() {
			return getRuleContext(Field_typeContext.class,0);
		}
		public Function_typeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_function_type; }
	}

	public final Function_typeContext function_type() throws RecognitionException {
		Function_typeContext _localctx = new Function_typeContext(_ctx, getState());
		enterRule(_localctx, 40, RULE_function_type);
		try {
			setState(286);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__27:
			case T__30:
			case T__31:
			case TYPE_BOOL:
			case TYPE_BYTE:
			case TYPE_I16:
			case TYPE_I32:
			case TYPE_I64:
			case TYPE_DOUBLE:
			case TYPE_STRING:
			case TYPE_BINARY:
			case IDENTIFIER:
				enterOuterAlt(_localctx, 1);
				{
				setState(284);
				field_type();
				}
				break;
			case T__25:
				enterOuterAlt(_localctx, 2);
				{
				setState(285);
				match(T__25);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Throws_listContext extends ParserRuleContext {
		public List<FieldContext> field() {
			return getRuleContexts(FieldContext.class);
		}
		public FieldContext field(int i) {
			return getRuleContext(FieldContext.class,i);
		}
		public Throws_listContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_throws_list; }
	}

	public final Throws_listContext throws_list() throws RecognitionException {
		Throws_listContext _localctx = new Throws_listContext(_ctx, getState());
		enterRule(_localctx, 42, RULE_throws_list);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(288);
			match(T__26);
			setState(289);
			match(T__21);
			setState(293);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__19) | (1L << T__20) | (1L << T__27) | (1L << T__30) | (1L << T__31) | (1L << INTEGER) | (1L << HEX_INTEGER) | (1L << TYPE_BOOL) | (1L << TYPE_BYTE) | (1L << TYPE_I16) | (1L << TYPE_I32) | (1L << TYPE_I64) | (1L << TYPE_DOUBLE) | (1L << TYPE_STRING) | (1L << TYPE_BINARY) | (1L << IDENTIFIER))) != 0)) {
				{
				{
				setState(290);
				field();
				}
				}
				setState(295);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(296);
			match(T__22);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Type_annotationsContext extends ParserRuleContext {
		public List<Type_annotationContext> type_annotation() {
			return getRuleContexts(Type_annotationContext.class);
		}
		public Type_annotationContext type_annotation(int i) {
			return getRuleContext(Type_annotationContext.class,i);
		}
		public Type_annotationsContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_type_annotations; }
	}

	public final Type_annotationsContext type_annotations() throws RecognitionException {
		Type_annotationsContext _localctx = new Type_annotationsContext(_ctx, getState());
		enterRule(_localctx, 44, RULE_type_annotations);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(298);
			match(T__21);
			setState(302);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==IDENTIFIER) {
				{
				{
				setState(299);
				type_annotation();
				}
				}
				setState(304);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(305);
			match(T__22);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Type_annotationContext extends ParserRuleContext {
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public Annotation_valueContext annotation_value() {
			return getRuleContext(Annotation_valueContext.class,0);
		}
		public List_separatorContext list_separator() {
			return getRuleContext(List_separatorContext.class,0);
		}
		public Type_annotationContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_type_annotation; }
	}

	public final Type_annotationContext type_annotation() throws RecognitionException {
		Type_annotationContext _localctx = new Type_annotationContext(_ctx, getState());
		enterRule(_localctx, 46, RULE_type_annotation);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(307);
			match(IDENTIFIER);
			setState(310);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__7) {
				{
				setState(308);
				match(T__7);
				setState(309);
				annotation_value();
				}
			}

			setState(313);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__35 || _la==COMMA) {
				{
				setState(312);
				list_separator();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Annotation_valueContext extends ParserRuleContext {
		public IntegerContext integer() {
			return getRuleContext(IntegerContext.class,0);
		}
		public TerminalNode LITERAL() { return getToken(ThriftGrammerParser.LITERAL, 0); }
		public Annotation_valueContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_annotation_value; }
	}

	public final Annotation_valueContext annotation_value() throws RecognitionException {
		Annotation_valueContext _localctx = new Annotation_valueContext(_ctx, getState());
		enterRule(_localctx, 48, RULE_annotation_value);
		try {
			setState(317);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case INTEGER:
			case HEX_INTEGER:
				enterOuterAlt(_localctx, 1);
				{
				setState(315);
				integer();
				}
				break;
			case LITERAL:
				enterOuterAlt(_localctx, 2);
				{
				setState(316);
				match(LITERAL);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Field_typeContext extends ParserRuleContext {
		public Base_typeContext base_type() {
			return getRuleContext(Base_typeContext.class,0);
		}
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public Container_typeContext container_type() {
			return getRuleContext(Container_typeContext.class,0);
		}
		public Field_typeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_field_type; }
	}

	public final Field_typeContext field_type() throws RecognitionException {
		Field_typeContext _localctx = new Field_typeContext(_ctx, getState());
		enterRule(_localctx, 50, RULE_field_type);
		try {
			setState(322);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case TYPE_BOOL:
			case TYPE_BYTE:
			case TYPE_I16:
			case TYPE_I32:
			case TYPE_I64:
			case TYPE_DOUBLE:
			case TYPE_STRING:
			case TYPE_BINARY:
				enterOuterAlt(_localctx, 1);
				{
				setState(319);
				base_type();
				}
				break;
			case IDENTIFIER:
				enterOuterAlt(_localctx, 2);
				{
				setState(320);
				match(IDENTIFIER);
				}
				break;
			case T__27:
			case T__30:
			case T__31:
				enterOuterAlt(_localctx, 3);
				{
				setState(321);
				container_type();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Base_typeContext extends ParserRuleContext {
		public Real_base_typeContext real_base_type() {
			return getRuleContext(Real_base_typeContext.class,0);
		}
		public Type_annotationsContext type_annotations() {
			return getRuleContext(Type_annotationsContext.class,0);
		}
		public Base_typeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_base_type; }
	}

	public final Base_typeContext base_type() throws RecognitionException {
		Base_typeContext _localctx = new Base_typeContext(_ctx, getState());
		enterRule(_localctx, 52, RULE_base_type);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(324);
			real_base_type();
			setState(326);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__21) {
				{
				setState(325);
				type_annotations();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Container_typeContext extends ParserRuleContext {
		public Map_typeContext map_type() {
			return getRuleContext(Map_typeContext.class,0);
		}
		public Set_typeContext set_type() {
			return getRuleContext(Set_typeContext.class,0);
		}
		public List_typeContext list_type() {
			return getRuleContext(List_typeContext.class,0);
		}
		public Type_annotationsContext type_annotations() {
			return getRuleContext(Type_annotationsContext.class,0);
		}
		public Container_typeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_container_type; }
	}

	public final Container_typeContext container_type() throws RecognitionException {
		Container_typeContext _localctx = new Container_typeContext(_ctx, getState());
		enterRule(_localctx, 54, RULE_container_type);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(331);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__27:
				{
				setState(328);
				map_type();
				}
				break;
			case T__30:
				{
				setState(329);
				set_type();
				}
				break;
			case T__31:
				{
				setState(330);
				list_type();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
			setState(334);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__21) {
				{
				setState(333);
				type_annotations();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Map_typeContext extends ParserRuleContext {
		public List<Field_typeContext> field_type() {
			return getRuleContexts(Field_typeContext.class);
		}
		public Field_typeContext field_type(int i) {
			return getRuleContext(Field_typeContext.class,i);
		}
		public TerminalNode COMMA() { return getToken(ThriftGrammerParser.COMMA, 0); }
		public Cpp_typeContext cpp_type() {
			return getRuleContext(Cpp_typeContext.class,0);
		}
		public Map_typeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_map_type; }
	}

	public final Map_typeContext map_type() throws RecognitionException {
		Map_typeContext _localctx = new Map_typeContext(_ctx, getState());
		enterRule(_localctx, 56, RULE_map_type);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(336);
			match(T__27);
			setState(338);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__32) {
				{
				setState(337);
				cpp_type();
				}
			}

			setState(340);
			match(T__28);
			setState(341);
			field_type();
			setState(342);
			match(COMMA);
			setState(343);
			field_type();
			setState(344);
			match(T__29);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Set_typeContext extends ParserRuleContext {
		public Field_typeContext field_type() {
			return getRuleContext(Field_typeContext.class,0);
		}
		public Cpp_typeContext cpp_type() {
			return getRuleContext(Cpp_typeContext.class,0);
		}
		public Set_typeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_set_type; }
	}

	public final Set_typeContext set_type() throws RecognitionException {
		Set_typeContext _localctx = new Set_typeContext(_ctx, getState());
		enterRule(_localctx, 58, RULE_set_type);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(346);
			match(T__30);
			setState(348);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__32) {
				{
				setState(347);
				cpp_type();
				}
			}

			setState(350);
			match(T__28);
			setState(351);
			field_type();
			setState(352);
			match(T__29);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class List_typeContext extends ParserRuleContext {
		public Field_typeContext field_type() {
			return getRuleContext(Field_typeContext.class,0);
		}
		public Cpp_typeContext cpp_type() {
			return getRuleContext(Cpp_typeContext.class,0);
		}
		public List_typeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_list_type; }
	}

	public final List_typeContext list_type() throws RecognitionException {
		List_typeContext _localctx = new List_typeContext(_ctx, getState());
		enterRule(_localctx, 60, RULE_list_type);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(354);
			match(T__31);
			setState(355);
			match(T__28);
			setState(356);
			field_type();
			setState(357);
			match(T__29);
			setState(359);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__32) {
				{
				setState(358);
				cpp_type();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Cpp_typeContext extends ParserRuleContext {
		public TerminalNode LITERAL() { return getToken(ThriftGrammerParser.LITERAL, 0); }
		public Cpp_typeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_cpp_type; }
	}

	public final Cpp_typeContext cpp_type() throws RecognitionException {
		Cpp_typeContext _localctx = new Cpp_typeContext(_ctx, getState());
		enterRule(_localctx, 62, RULE_cpp_type);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(361);
			match(T__32);
			setState(362);
			match(LITERAL);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Const_valueContext extends ParserRuleContext {
		public IntegerContext integer() {
			return getRuleContext(IntegerContext.class,0);
		}
		public TerminalNode DOUBLE() { return getToken(ThriftGrammerParser.DOUBLE, 0); }
		public TerminalNode LITERAL() { return getToken(ThriftGrammerParser.LITERAL, 0); }
		public TerminalNode IDENTIFIER() { return getToken(ThriftGrammerParser.IDENTIFIER, 0); }
		public Const_listContext const_list() {
			return getRuleContext(Const_listContext.class,0);
		}
		public Const_mapContext const_map() {
			return getRuleContext(Const_mapContext.class,0);
		}
		public Const_valueContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_const_value; }
	}

	public final Const_valueContext const_value() throws RecognitionException {
		Const_valueContext _localctx = new Const_valueContext(_ctx, getState());
		enterRule(_localctx, 64, RULE_const_value);
		try {
			setState(370);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case INTEGER:
			case HEX_INTEGER:
				enterOuterAlt(_localctx, 1);
				{
				setState(364);
				integer();
				}
				break;
			case DOUBLE:
				enterOuterAlt(_localctx, 2);
				{
				setState(365);
				match(DOUBLE);
				}
				break;
			case LITERAL:
				enterOuterAlt(_localctx, 3);
				{
				setState(366);
				match(LITERAL);
				}
				break;
			case IDENTIFIER:
				enterOuterAlt(_localctx, 4);
				{
				setState(367);
				match(IDENTIFIER);
				}
				break;
			case T__33:
				enterOuterAlt(_localctx, 5);
				{
				setState(368);
				const_list();
				}
				break;
			case T__10:
				enterOuterAlt(_localctx, 6);
				{
				setState(369);
				const_map();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class IntegerContext extends ParserRuleContext {
		public TerminalNode INTEGER() { return getToken(ThriftGrammerParser.INTEGER, 0); }
		public TerminalNode HEX_INTEGER() { return getToken(ThriftGrammerParser.HEX_INTEGER, 0); }
		public IntegerContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_integer; }
	}

	public final IntegerContext integer() throws RecognitionException {
		IntegerContext _localctx = new IntegerContext(_ctx, getState());
		enterRule(_localctx, 66, RULE_integer);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(372);
			_la = _input.LA(1);
			if ( !(_la==INTEGER || _la==HEX_INTEGER) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Const_listContext extends ParserRuleContext {
		public List<Const_valueContext> const_value() {
			return getRuleContexts(Const_valueContext.class);
		}
		public Const_valueContext const_value(int i) {
			return getRuleContext(Const_valueContext.class,i);
		}
		public List<List_separatorContext> list_separator() {
			return getRuleContexts(List_separatorContext.class);
		}
		public List_separatorContext list_separator(int i) {
			return getRuleContext(List_separatorContext.class,i);
		}
		public Const_listContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_const_list; }
	}

	public final Const_listContext const_list() throws RecognitionException {
		Const_listContext _localctx = new Const_listContext(_ctx, getState());
		enterRule(_localctx, 68, RULE_const_list);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(374);
			match(T__33);
			setState(381);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__10) | (1L << T__33) | (1L << INTEGER) | (1L << HEX_INTEGER) | (1L << DOUBLE) | (1L << LITERAL) | (1L << IDENTIFIER))) != 0)) {
				{
				{
				setState(375);
				const_value();
				setState(377);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==T__35 || _la==COMMA) {
					{
					setState(376);
					list_separator();
					}
				}

				}
				}
				setState(383);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(384);
			match(T__34);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Const_map_entryContext extends ParserRuleContext {
		public List<Const_valueContext> const_value() {
			return getRuleContexts(Const_valueContext.class);
		}
		public Const_valueContext const_value(int i) {
			return getRuleContext(Const_valueContext.class,i);
		}
		public List_separatorContext list_separator() {
			return getRuleContext(List_separatorContext.class,0);
		}
		public Const_map_entryContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_const_map_entry; }
	}

	public final Const_map_entryContext const_map_entry() throws RecognitionException {
		Const_map_entryContext _localctx = new Const_map_entryContext(_ctx, getState());
		enterRule(_localctx, 70, RULE_const_map_entry);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(386);
			const_value();
			setState(387);
			match(T__18);
			setState(388);
			const_value();
			setState(390);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__35 || _la==COMMA) {
				{
				setState(389);
				list_separator();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Const_mapContext extends ParserRuleContext {
		public List<Const_map_entryContext> const_map_entry() {
			return getRuleContexts(Const_map_entryContext.class);
		}
		public Const_map_entryContext const_map_entry(int i) {
			return getRuleContext(Const_map_entryContext.class,i);
		}
		public Const_mapContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_const_map; }
	}

	public final Const_mapContext const_map() throws RecognitionException {
		Const_mapContext _localctx = new Const_mapContext(_ctx, getState());
		enterRule(_localctx, 72, RULE_const_map);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(392);
			match(T__10);
			setState(396);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__10) | (1L << T__33) | (1L << INTEGER) | (1L << HEX_INTEGER) | (1L << DOUBLE) | (1L << LITERAL) | (1L << IDENTIFIER))) != 0)) {
				{
				{
				setState(393);
				const_map_entry();
				}
				}
				setState(398);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(399);
			match(T__11);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class List_separatorContext extends ParserRuleContext {
		public TerminalNode COMMA() { return getToken(ThriftGrammerParser.COMMA, 0); }
		public List_separatorContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_list_separator; }
	}

	public final List_separatorContext list_separator() throws RecognitionException {
		List_separatorContext _localctx = new List_separatorContext(_ctx, getState());
		enterRule(_localctx, 74, RULE_list_separator);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(401);
			_la = _input.LA(1);
			if ( !(_la==T__35 || _la==COMMA) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Real_base_typeContext extends ParserRuleContext {
		public TerminalNode TYPE_BOOL() { return getToken(ThriftGrammerParser.TYPE_BOOL, 0); }
		public TerminalNode TYPE_BYTE() { return getToken(ThriftGrammerParser.TYPE_BYTE, 0); }
		public TerminalNode TYPE_I16() { return getToken(ThriftGrammerParser.TYPE_I16, 0); }
		public TerminalNode TYPE_I32() { return getToken(ThriftGrammerParser.TYPE_I32, 0); }
		public TerminalNode TYPE_I64() { return getToken(ThriftGrammerParser.TYPE_I64, 0); }
		public TerminalNode TYPE_DOUBLE() { return getToken(ThriftGrammerParser.TYPE_DOUBLE, 0); }
		public TerminalNode TYPE_STRING() { return getToken(ThriftGrammerParser.TYPE_STRING, 0); }
		public TerminalNode TYPE_BINARY() { return getToken(ThriftGrammerParser.TYPE_BINARY, 0); }
		public Real_base_typeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_real_base_type; }
	}

	public final Real_base_typeContext real_base_type() throws RecognitionException {
		Real_base_typeContext _localctx = new Real_base_typeContext(_ctx, getState());
		enterRule(_localctx, 76, RULE_real_base_type);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(403);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << TYPE_BOOL) | (1L << TYPE_BYTE) | (1L << TYPE_I16) | (1L << TYPE_I32) | (1L << TYPE_I64) | (1L << TYPE_DOUBLE) | (1L << TYPE_STRING) | (1L << TYPE_BINARY))) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static final String _serializedATN =
		"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\67\u0198\4\2\t\2"+
		"\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13"+
		"\t\13\4\f\t\f\4\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22"+
		"\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30\4\31\t\31"+
		"\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36\t\36\4\37\t\37\4 \t \4!"+
		"\t!\4\"\t\"\4#\t#\4$\t$\4%\t%\4&\t&\4\'\t\'\4(\t(\3\2\7\2R\n\2\f\2\16"+
		"\2U\13\2\3\2\7\2X\n\2\f\2\16\2[\13\2\3\2\3\2\3\3\3\3\3\3\5\3b\n\3\3\4"+
		"\3\4\3\4\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\3\5\5\5q\n\5\3\6\3\6\3\6"+
		"\3\7\3\7\3\7\3\7\3\7\3\7\3\7\3\7\5\7~\n\7\3\b\3\b\3\b\3\b\3\b\5\b\u0085"+
		"\n\b\3\b\5\b\u0088\n\b\3\t\3\t\3\t\3\t\5\t\u008e\n\t\3\n\3\n\3\n\3\n\7"+
		"\n\u0094\n\n\f\n\16\n\u0097\13\n\3\n\3\n\5\n\u009b\n\n\3\13\3\13\3\13"+
		"\5\13\u00a0\n\13\3\13\5\13\u00a3\n\13\3\13\5\13\u00a6\n\13\3\f\3\f\3\f"+
		"\3\f\3\f\5\f\u00ad\n\f\7\f\u00af\n\f\f\f\16\f\u00b2\13\f\3\f\3\f\5\f\u00b6"+
		"\n\f\3\r\3\r\3\r\3\r\7\r\u00bc\n\r\f\r\16\r\u00bf\13\r\3\r\3\r\5\r\u00c3"+
		"\n\r\3\16\3\16\3\16\3\16\7\16\u00c9\n\16\f\16\16\16\u00cc\13\16\3\16\3"+
		"\16\5\16\u00d0\n\16\3\17\3\17\3\17\3\17\7\17\u00d6\n\17\f\17\16\17\u00d9"+
		"\13\17\3\17\3\17\5\17\u00dd\n\17\3\20\3\20\3\20\3\20\5\20\u00e3\n\20\3"+
		"\20\3\20\7\20\u00e7\n\20\f\20\16\20\u00ea\13\20\3\20\3\20\5\20\u00ee\n"+
		"\20\3\21\5\21\u00f1\n\21\3\21\5\21\u00f4\n\21\3\21\3\21\3\21\3\21\5\21"+
		"\u00fa\n\21\3\21\5\21\u00fd\n\21\3\21\5\21\u0100\n\21\3\22\3\22\3\22\3"+
		"\23\3\23\3\24\5\24\u0108\n\24\3\24\3\24\3\24\3\24\7\24\u010e\n\24\f\24"+
		"\16\24\u0111\13\24\3\24\3\24\5\24\u0115\n\24\3\24\5\24\u0118\n\24\3\24"+
		"\5\24\u011b\n\24\3\25\3\25\3\26\3\26\5\26\u0121\n\26\3\27\3\27\3\27\7"+
		"\27\u0126\n\27\f\27\16\27\u0129\13\27\3\27\3\27\3\30\3\30\7\30\u012f\n"+
		"\30\f\30\16\30\u0132\13\30\3\30\3\30\3\31\3\31\3\31\5\31\u0139\n\31\3"+
		"\31\5\31\u013c\n\31\3\32\3\32\5\32\u0140\n\32\3\33\3\33\3\33\5\33\u0145"+
		"\n\33\3\34\3\34\5\34\u0149\n\34\3\35\3\35\3\35\5\35\u014e\n\35\3\35\5"+
		"\35\u0151\n\35\3\36\3\36\5\36\u0155\n\36\3\36\3\36\3\36\3\36\3\36\3\36"+
		"\3\37\3\37\5\37\u015f\n\37\3\37\3\37\3\37\3\37\3 \3 \3 \3 \3 \5 \u016a"+
		"\n \3!\3!\3!\3\"\3\"\3\"\3\"\3\"\3\"\5\"\u0175\n\"\3#\3#\3$\3$\3$\5$\u017c"+
		"\n$\7$\u017e\n$\f$\16$\u0181\13$\3$\3$\3%\3%\3%\3%\5%\u0189\n%\3&\3&\7"+
		"&\u018d\n&\f&\16&\u0190\13&\3&\3&\3\'\3\'\3(\3(\3(\2\2)\2\4\6\b\n\f\16"+
		"\20\22\24\26\30\32\34\36 \"$&(*,.\60\62\64\668:<>@BDFHJLN\2\b\3\2\62\63"+
		"\3\2\26\27\3\2\32\33\3\2\'(\4\2&&\64\64\3\2*\61\2\u01b4\2S\3\2\2\2\4a"+
		"\3\2\2\2\6c\3\2\2\2\bp\3\2\2\2\nr\3\2\2\2\f}\3\2\2\2\16\177\3\2\2\2\20"+
		"\u0089\3\2\2\2\22\u008f\3\2\2\2\24\u009c\3\2\2\2\26\u00a7\3\2\2\2\30\u00b7"+
		"\3\2\2\2\32\u00c4\3\2\2\2\34\u00d1\3\2\2\2\36\u00de\3\2\2\2 \u00f0\3\2"+
		"\2\2\"\u0101\3\2\2\2$\u0104\3\2\2\2&\u0107\3\2\2\2(\u011c\3\2\2\2*\u0120"+
		"\3\2\2\2,\u0122\3\2\2\2.\u012c\3\2\2\2\60\u0135\3\2\2\2\62\u013f\3\2\2"+
		"\2\64\u0144\3\2\2\2\66\u0146\3\2\2\28\u014d\3\2\2\2:\u0152\3\2\2\2<\u015c"+
		"\3\2\2\2>\u0164\3\2\2\2@\u016b\3\2\2\2B\u0174\3\2\2\2D\u0176\3\2\2\2F"+
		"\u0178\3\2\2\2H\u0184\3\2\2\2J\u018a\3\2\2\2L\u0193\3\2\2\2N\u0195\3\2"+
		"\2\2PR\5\4\3\2QP\3\2\2\2RU\3\2\2\2SQ\3\2\2\2ST\3\2\2\2TY\3\2\2\2US\3\2"+
		"\2\2VX\5\f\7\2WV\3\2\2\2X[\3\2\2\2YW\3\2\2\2YZ\3\2\2\2Z\\\3\2\2\2[Y\3"+
		"\2\2\2\\]\7\2\2\3]\3\3\2\2\2^b\5\6\4\2_b\5\b\5\2`b\5\n\6\2a^\3\2\2\2a"+
		"_\3\2\2\2a`\3\2\2\2b\5\3\2\2\2cd\7\3\2\2de\7\62\2\2e\7\3\2\2\2fg\7\4\2"+
		"\2gh\7\5\2\2hq\t\2\2\2ij\7\4\2\2jk\7\63\2\2kq\t\2\2\2lm\7\6\2\2mq\7\63"+
		"\2\2no\7\7\2\2oq\7\63\2\2pf\3\2\2\2pi\3\2\2\2pl\3\2\2\2pn\3\2\2\2q\t\3"+
		"\2\2\2rs\7\b\2\2st\7\62\2\2t\13\3\2\2\2u~\5\16\b\2v~\5\20\t\2w~\5\22\n"+
		"\2x~\5\26\f\2y~\5\30\r\2z~\5\32\16\2{~\5\34\17\2|~\5\36\20\2}u\3\2\2\2"+
		"}v\3\2\2\2}w\3\2\2\2}x\3\2\2\2}y\3\2\2\2}z\3\2\2\2}{\3\2\2\2}|\3\2\2\2"+
		"~\r\3\2\2\2\177\u0080\7\t\2\2\u0080\u0081\5\64\33\2\u0081\u0084\7\63\2"+
		"\2\u0082\u0083\7\n\2\2\u0083\u0085\5B\"\2\u0084\u0082\3\2\2\2\u0084\u0085"+
		"\3\2\2\2\u0085\u0087\3\2\2\2\u0086\u0088\5L\'\2\u0087\u0086\3\2\2\2\u0087"+
		"\u0088\3\2\2\2\u0088\17\3\2\2\2\u0089\u008a\7\13\2\2\u008a\u008b\5\64"+
		"\33\2\u008b\u008d\7\63\2\2\u008c\u008e\5.\30\2\u008d\u008c\3\2\2\2\u008d"+
		"\u008e\3\2\2\2\u008e\21\3\2\2\2\u008f\u0090\7\f\2\2\u0090\u0091\7\63\2"+
		"\2\u0091\u0095\7\r\2\2\u0092\u0094\5\24\13\2\u0093\u0092\3\2\2\2\u0094"+
		"\u0097\3\2\2\2\u0095\u0093\3\2\2\2\u0095\u0096\3\2\2\2\u0096\u0098\3\2"+
		"\2\2\u0097\u0095\3\2\2\2\u0098\u009a\7\16\2\2\u0099\u009b\5.\30\2\u009a"+
		"\u0099\3\2\2\2\u009a\u009b\3\2\2\2\u009b\23\3\2\2\2\u009c\u009f\7\63\2"+
		"\2\u009d\u009e\7\n\2\2\u009e\u00a0\5D#\2\u009f\u009d\3\2\2\2\u009f\u00a0"+
		"\3\2\2\2\u00a0\u00a2\3\2\2\2\u00a1\u00a3\5.\30\2\u00a2\u00a1\3\2\2\2\u00a2"+
		"\u00a3\3\2\2\2\u00a3\u00a5\3\2\2\2\u00a4\u00a6\5L\'\2\u00a5\u00a4\3\2"+
		"\2\2\u00a5\u00a6\3\2\2\2\u00a6\25\3\2\2\2\u00a7\u00a8\7\17\2\2\u00a8\u00a9"+
		"\7\63\2\2\u00a9\u00b0\7\r\2\2\u00aa\u00ac\7\62\2\2\u00ab\u00ad\5L\'\2"+
		"\u00ac\u00ab\3\2\2\2\u00ac\u00ad\3\2\2\2\u00ad\u00af\3\2\2\2\u00ae\u00aa"+
		"\3\2\2\2\u00af\u00b2\3\2\2\2\u00b0\u00ae\3\2\2\2\u00b0\u00b1\3\2\2\2\u00b1"+
		"\u00b3\3\2\2\2\u00b2\u00b0\3\2\2\2\u00b3\u00b5\7\16\2\2\u00b4\u00b6\5"+
		".\30\2\u00b5\u00b4\3\2\2\2\u00b5\u00b6\3\2\2\2\u00b6\27\3\2\2\2\u00b7"+
		"\u00b8\7\20\2\2\u00b8\u00b9\7\63\2\2\u00b9\u00bd\7\r\2\2\u00ba\u00bc\5"+
		" \21\2\u00bb\u00ba\3\2\2\2\u00bc\u00bf\3\2\2\2\u00bd\u00bb\3\2\2\2\u00bd"+
		"\u00be\3\2\2\2\u00be\u00c0\3\2\2\2\u00bf\u00bd\3\2\2\2\u00c0\u00c2\7\16"+
		"\2\2\u00c1\u00c3\5.\30\2\u00c2\u00c1\3\2\2\2\u00c2\u00c3\3\2\2\2\u00c3"+
		"\31\3\2\2\2\u00c4\u00c5\7\21\2\2\u00c5\u00c6\7\63\2\2\u00c6\u00ca\7\r"+
		"\2\2\u00c7\u00c9\5 \21\2\u00c8\u00c7\3\2\2\2\u00c9\u00cc\3\2\2\2\u00ca"+
		"\u00c8\3\2\2\2\u00ca\u00cb\3\2\2\2\u00cb\u00cd\3\2\2\2\u00cc\u00ca\3\2"+
		"\2\2\u00cd\u00cf\7\16\2\2\u00ce\u00d0\5.\30\2\u00cf\u00ce\3\2\2\2\u00cf"+
		"\u00d0\3\2\2\2\u00d0\33\3\2\2\2\u00d1\u00d2\7\22\2\2\u00d2\u00d3\7\63"+
		"\2\2\u00d3\u00d7\7\r\2\2\u00d4\u00d6\5 \21\2\u00d5\u00d4\3\2\2\2\u00d6"+
		"\u00d9\3\2\2\2\u00d7\u00d5\3\2\2\2\u00d7\u00d8\3\2\2\2\u00d8\u00da\3\2"+
		"\2\2\u00d9\u00d7\3\2\2\2\u00da\u00dc\7\16\2\2\u00db\u00dd\5.\30\2\u00dc"+
		"\u00db\3\2\2\2\u00dc\u00dd\3\2\2\2\u00dd\35\3\2\2\2\u00de\u00df\7\23\2"+
		"\2\u00df\u00e2\7\63\2\2\u00e0\u00e1\7\24\2\2\u00e1\u00e3\7\63\2\2\u00e2"+
		"\u00e0\3\2\2\2\u00e2\u00e3\3\2\2\2\u00e3\u00e4\3\2\2\2\u00e4\u00e8\7\r"+
		"\2\2\u00e5\u00e7\5&\24\2\u00e6\u00e5\3\2\2\2\u00e7\u00ea\3\2\2\2\u00e8"+
		"\u00e6\3\2\2\2\u00e8\u00e9\3\2\2\2\u00e9\u00eb\3\2\2\2\u00ea\u00e8\3\2"+
		"\2\2\u00eb\u00ed\7\16\2\2\u00ec\u00ee\5.\30\2\u00ed\u00ec\3\2\2\2\u00ed"+
		"\u00ee\3\2\2\2\u00ee\37\3\2\2\2\u00ef\u00f1\5\"\22\2\u00f0\u00ef\3\2\2"+
		"\2\u00f0\u00f1\3\2\2\2\u00f1\u00f3\3\2\2\2\u00f2\u00f4\5$\23\2\u00f3\u00f2"+
		"\3\2\2\2\u00f3\u00f4\3\2\2\2\u00f4\u00f5\3\2\2\2\u00f5\u00f6\5\64\33\2"+
		"\u00f6\u00f9\7\63\2\2\u00f7\u00f8\7\n\2\2\u00f8\u00fa\5B\"\2\u00f9\u00f7"+
		"\3\2\2\2\u00f9\u00fa\3\2\2\2\u00fa\u00fc\3\2\2\2\u00fb\u00fd\5.\30\2\u00fc"+
		"\u00fb\3\2\2\2\u00fc\u00fd\3\2\2\2\u00fd\u00ff\3\2\2\2\u00fe\u0100\5L"+
		"\'\2\u00ff\u00fe\3\2\2\2\u00ff\u0100\3\2\2\2\u0100!\3\2\2\2\u0101\u0102"+
		"\5D#\2\u0102\u0103\7\25\2\2\u0103#\3\2\2\2\u0104\u0105\t\3\2\2\u0105%"+
		"\3\2\2\2\u0106\u0108\5(\25\2\u0107\u0106\3\2\2\2\u0107\u0108\3\2\2\2\u0108"+
		"\u0109\3\2\2\2\u0109\u010a\5*\26\2\u010a\u010b\7\63\2\2\u010b\u010f\7"+
		"\30\2\2\u010c\u010e\5 \21\2\u010d\u010c\3\2\2\2\u010e\u0111\3\2\2\2\u010f"+
		"\u010d\3\2\2\2\u010f\u0110\3\2\2\2\u0110\u0112\3\2\2\2\u0111\u010f\3\2"+
		"\2\2\u0112\u0114\7\31\2\2\u0113\u0115\5,\27\2\u0114\u0113\3\2\2\2\u0114"+
		"\u0115\3\2\2\2\u0115\u0117\3\2\2\2\u0116\u0118\5.\30\2\u0117\u0116\3\2"+
		"\2\2\u0117\u0118\3\2\2\2\u0118\u011a\3\2\2\2\u0119\u011b\5L\'\2\u011a"+
		"\u0119\3\2\2\2\u011a\u011b\3\2\2\2\u011b\'\3\2\2\2\u011c\u011d\t\4\2\2"+
		"\u011d)\3\2\2\2\u011e\u0121\5\64\33\2\u011f\u0121\7\34\2\2\u0120\u011e"+
		"\3\2\2\2\u0120\u011f\3\2\2\2\u0121+\3\2\2\2\u0122\u0123\7\35\2\2\u0123"+
		"\u0127\7\30\2\2\u0124\u0126\5 \21\2\u0125\u0124\3\2\2\2\u0126\u0129\3"+
		"\2\2\2\u0127\u0125\3\2\2\2\u0127\u0128\3\2\2\2\u0128\u012a\3\2\2\2\u0129"+
		"\u0127\3\2\2\2\u012a\u012b\7\31\2\2\u012b-\3\2\2\2\u012c\u0130\7\30\2"+
		"\2\u012d\u012f\5\60\31\2\u012e\u012d\3\2\2\2\u012f\u0132\3\2\2\2\u0130"+
		"\u012e\3\2\2\2\u0130\u0131\3\2\2\2\u0131\u0133\3\2\2\2\u0132\u0130\3\2"+
		"\2\2\u0133\u0134\7\31\2\2\u0134/\3\2\2\2\u0135\u0138\7\63\2\2\u0136\u0137"+
		"\7\n\2\2\u0137\u0139\5\62\32\2\u0138\u0136\3\2\2\2\u0138\u0139\3\2\2\2"+
		"\u0139\u013b\3\2\2\2\u013a\u013c\5L\'\2\u013b\u013a\3\2\2\2\u013b\u013c"+
		"\3\2\2\2\u013c\61\3\2\2\2\u013d\u0140\5D#\2\u013e\u0140\7\62\2\2\u013f"+
		"\u013d\3\2\2\2\u013f\u013e\3\2\2\2\u0140\63\3\2\2\2\u0141\u0145\5\66\34"+
		"\2\u0142\u0145\7\63\2\2\u0143\u0145\58\35\2\u0144\u0141\3\2\2\2\u0144"+
		"\u0142\3\2\2\2\u0144\u0143\3\2\2\2\u0145\65\3\2\2\2\u0146\u0148\5N(\2"+
		"\u0147\u0149\5.\30\2\u0148\u0147\3\2\2\2\u0148\u0149\3\2\2\2\u0149\67"+
		"\3\2\2\2\u014a\u014e\5:\36\2\u014b\u014e\5<\37\2\u014c\u014e\5> \2\u014d"+
		"\u014a\3\2\2\2\u014d\u014b\3\2\2\2\u014d\u014c\3\2\2\2\u014e\u0150\3\2"+
		"\2\2\u014f\u0151\5.\30\2\u0150\u014f\3\2\2\2\u0150\u0151\3\2\2\2\u0151"+
		"9\3\2\2\2\u0152\u0154\7\36\2\2\u0153\u0155\5@!\2\u0154\u0153\3\2\2\2\u0154"+
		"\u0155\3\2\2\2\u0155\u0156\3\2\2\2\u0156\u0157\7\37\2\2\u0157\u0158\5"+
		"\64\33\2\u0158\u0159\7\64\2\2\u0159\u015a\5\64\33\2\u015a\u015b\7 \2\2"+
		"\u015b;\3\2\2\2\u015c\u015e\7!\2\2\u015d\u015f\5@!\2\u015e\u015d\3\2\2"+
		"\2\u015e\u015f\3\2\2\2\u015f\u0160\3\2\2\2\u0160\u0161\7\37\2\2\u0161"+
		"\u0162\5\64\33\2\u0162\u0163\7 \2\2\u0163=\3\2\2\2\u0164\u0165\7\"\2\2"+
		"\u0165\u0166\7\37\2\2\u0166\u0167\5\64\33\2\u0167\u0169\7 \2\2\u0168\u016a"+
		"\5@!\2\u0169\u0168\3\2\2\2\u0169\u016a\3\2\2\2\u016a?\3\2\2\2\u016b\u016c"+
		"\7#\2\2\u016c\u016d\7\62\2\2\u016dA\3\2\2\2\u016e\u0175\5D#\2\u016f\u0175"+
		"\7)\2\2\u0170\u0175\7\62\2\2\u0171\u0175\7\63\2\2\u0172\u0175\5F$\2\u0173"+
		"\u0175\5J&\2\u0174\u016e\3\2\2\2\u0174\u016f\3\2\2\2\u0174\u0170\3\2\2"+
		"\2\u0174\u0171\3\2\2\2\u0174\u0172\3\2\2\2\u0174\u0173\3\2\2\2\u0175C"+
		"\3\2\2\2\u0176\u0177\t\5\2\2\u0177E\3\2\2\2\u0178\u017f\7$\2\2\u0179\u017b"+
		"\5B\"\2\u017a\u017c\5L\'\2\u017b\u017a\3\2\2\2\u017b\u017c\3\2\2\2\u017c"+
		"\u017e\3\2\2\2\u017d\u0179\3\2\2\2\u017e\u0181\3\2\2\2\u017f\u017d\3\2"+
		"\2\2\u017f\u0180\3\2\2\2\u0180\u0182\3\2\2\2\u0181\u017f\3\2\2\2\u0182"+
		"\u0183\7%\2\2\u0183G\3\2\2\2\u0184\u0185\5B\"\2\u0185\u0186\7\25\2\2\u0186"+
		"\u0188\5B\"\2\u0187\u0189\5L\'\2\u0188\u0187\3\2\2\2\u0188\u0189\3\2\2"+
		"\2\u0189I\3\2\2\2\u018a\u018e\7\r\2\2\u018b\u018d\5H%\2\u018c\u018b\3"+
		"\2\2\2\u018d\u0190\3\2\2\2\u018e\u018c\3\2\2\2\u018e\u018f\3\2\2\2\u018f"+
		"\u0191\3\2\2\2\u0190\u018e\3\2\2\2\u0191\u0192\7\16\2\2\u0192K\3\2\2\2"+
		"\u0193\u0194\t\6\2\2\u0194M\3\2\2\2\u0195\u0196\t\7\2\2\u0196O\3\2\2\2"+
		"\67SYap}\u0084\u0087\u008d\u0095\u009a\u009f\u00a2\u00a5\u00ac\u00b0\u00b5"+
		"\u00bd\u00c2\u00ca\u00cf\u00d7\u00dc\u00e2\u00e8\u00ed\u00f0\u00f3\u00f9"+
		"\u00fc\u00ff\u0107\u010f\u0114\u0117\u011a\u0120\u0127\u0130\u0138\u013b"+
		"\u013f\u0144\u0148\u014d\u0150\u0154\u015e\u0169\u0174\u017b\u017f\u0188"+
		"\u018e";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}