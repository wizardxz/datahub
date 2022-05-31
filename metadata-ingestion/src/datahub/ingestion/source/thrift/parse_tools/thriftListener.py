# Generated from thrift.g4 by ANTLR 4.7.2
from antlr4 import *

if __name__ is not None and "." in __name__:
    from .thriftParser import thriftParser
else:
    from thriftParser import thriftParser

# This class defines a complete listener for a parse tree produced by thriftParser.
class thriftListener(ParseTreeListener):

    # Enter a parse tree produced by thriftParser#document.
    def enterDocument(self, ctx: thriftParser.DocumentContext):
        pass

    # Exit a parse tree produced by thriftParser#document.
    def exitDocument(self, ctx: thriftParser.DocumentContext):
        pass

    # Enter a parse tree produced by thriftParser#header.
    def enterHeader(self, ctx: thriftParser.HeaderContext):
        pass

    # Exit a parse tree produced by thriftParser#header.
    def exitHeader(self, ctx: thriftParser.HeaderContext):
        pass

    # Enter a parse tree produced by thriftParser#include_.
    def enterInclude_(self, ctx: thriftParser.Include_Context):
        pass

    # Exit a parse tree produced by thriftParser#include_.
    def exitInclude_(self, ctx: thriftParser.Include_Context):
        pass

    # Enter a parse tree produced by thriftParser#starNamespace.
    def enterStarNamespace(self, ctx: thriftParser.StarNamespaceContext):
        pass

    # Exit a parse tree produced by thriftParser#starNamespace.
    def exitStarNamespace(self, ctx: thriftParser.StarNamespaceContext):
        pass

    # Enter a parse tree produced by thriftParser#explicitNamespace.
    def enterExplicitNamespace(self, ctx: thriftParser.ExplicitNamespaceContext):
        pass

    # Exit a parse tree produced by thriftParser#explicitNamespace.
    def exitExplicitNamespace(self, ctx: thriftParser.ExplicitNamespaceContext):
        pass

    # Enter a parse tree produced by thriftParser#cppNamespace.
    def enterCppNamespace(self, ctx: thriftParser.CppNamespaceContext):
        pass

    # Exit a parse tree produced by thriftParser#cppNamespace.
    def exitCppNamespace(self, ctx: thriftParser.CppNamespaceContext):
        pass

    # Enter a parse tree produced by thriftParser#phpNamespace.
    def enterPhpNamespace(self, ctx: thriftParser.PhpNamespaceContext):
        pass

    # Exit a parse tree produced by thriftParser#phpNamespace.
    def exitPhpNamespace(self, ctx: thriftParser.PhpNamespaceContext):
        pass

    # Enter a parse tree produced by thriftParser#cpp_include.
    def enterCpp_include(self, ctx: thriftParser.Cpp_includeContext):
        pass

    # Exit a parse tree produced by thriftParser#cpp_include.
    def exitCpp_include(self, ctx: thriftParser.Cpp_includeContext):
        pass

    # Enter a parse tree produced by thriftParser#definition.
    def enterDefinition(self, ctx: thriftParser.DefinitionContext):
        pass

    # Exit a parse tree produced by thriftParser#definition.
    def exitDefinition(self, ctx: thriftParser.DefinitionContext):
        pass

    # Enter a parse tree produced by thriftParser#const_rule.
    def enterConst_rule(self, ctx: thriftParser.Const_ruleContext):
        pass

    # Exit a parse tree produced by thriftParser#const_rule.
    def exitConst_rule(self, ctx: thriftParser.Const_ruleContext):
        pass

    # Enter a parse tree produced by thriftParser#typedef_.
    def enterTypedef_(self, ctx: thriftParser.Typedef_Context):
        pass

    # Exit a parse tree produced by thriftParser#typedef_.
    def exitTypedef_(self, ctx: thriftParser.Typedef_Context):
        pass

    # Enter a parse tree produced by thriftParser#enum_rule.
    def enterEnum_rule(self, ctx: thriftParser.Enum_ruleContext):
        pass

    # Exit a parse tree produced by thriftParser#enum_rule.
    def exitEnum_rule(self, ctx: thriftParser.Enum_ruleContext):
        pass

    # Enter a parse tree produced by thriftParser#enum_field.
    def enterEnum_field(self, ctx: thriftParser.Enum_fieldContext):
        pass

    # Exit a parse tree produced by thriftParser#enum_field.
    def exitEnum_field(self, ctx: thriftParser.Enum_fieldContext):
        pass

    # Enter a parse tree produced by thriftParser#senum.
    def enterSenum(self, ctx: thriftParser.SenumContext):
        pass

    # Exit a parse tree produced by thriftParser#senum.
    def exitSenum(self, ctx: thriftParser.SenumContext):
        pass

    # Enter a parse tree produced by thriftParser#struct_.
    def enterStruct_(self, ctx: thriftParser.Struct_Context):
        pass

    # Exit a parse tree produced by thriftParser#struct_.
    def exitStruct_(self, ctx: thriftParser.Struct_Context):
        pass

    # Enter a parse tree produced by thriftParser#union_.
    def enterUnion_(self, ctx: thriftParser.Union_Context):
        pass

    # Exit a parse tree produced by thriftParser#union_.
    def exitUnion_(self, ctx: thriftParser.Union_Context):
        pass

    # Enter a parse tree produced by thriftParser#exception_.
    def enterException_(self, ctx: thriftParser.Exception_Context):
        pass

    # Exit a parse tree produced by thriftParser#exception_.
    def exitException_(self, ctx: thriftParser.Exception_Context):
        pass

    # Enter a parse tree produced by thriftParser#service.
    def enterService(self, ctx: thriftParser.ServiceContext):
        pass

    # Exit a parse tree produced by thriftParser#service.
    def exitService(self, ctx: thriftParser.ServiceContext):
        pass

    # Enter a parse tree produced by thriftParser#field.
    def enterField(self, ctx: thriftParser.FieldContext):
        pass

    # Exit a parse tree produced by thriftParser#field.
    def exitField(self, ctx: thriftParser.FieldContext):
        pass

    # Enter a parse tree produced by thriftParser#field_id.
    def enterField_id(self, ctx: thriftParser.Field_idContext):
        pass

    # Exit a parse tree produced by thriftParser#field_id.
    def exitField_id(self, ctx: thriftParser.Field_idContext):
        pass

    # Enter a parse tree produced by thriftParser#field_req.
    def enterField_req(self, ctx: thriftParser.Field_reqContext):
        pass

    # Exit a parse tree produced by thriftParser#field_req.
    def exitField_req(self, ctx: thriftParser.Field_reqContext):
        pass

    # Enter a parse tree produced by thriftParser#function_.
    def enterFunction_(self, ctx: thriftParser.Function_Context):
        pass

    # Exit a parse tree produced by thriftParser#function_.
    def exitFunction_(self, ctx: thriftParser.Function_Context):
        pass

    # Enter a parse tree produced by thriftParser#oneway.
    def enterOneway(self, ctx: thriftParser.OnewayContext):
        pass

    # Exit a parse tree produced by thriftParser#oneway.
    def exitOneway(self, ctx: thriftParser.OnewayContext):
        pass

    # Enter a parse tree produced by thriftParser#function_type.
    def enterFunction_type(self, ctx: thriftParser.Function_typeContext):
        pass

    # Exit a parse tree produced by thriftParser#function_type.
    def exitFunction_type(self, ctx: thriftParser.Function_typeContext):
        pass

    # Enter a parse tree produced by thriftParser#throws_list.
    def enterThrows_list(self, ctx: thriftParser.Throws_listContext):
        pass

    # Exit a parse tree produced by thriftParser#throws_list.
    def exitThrows_list(self, ctx: thriftParser.Throws_listContext):
        pass

    # Enter a parse tree produced by thriftParser#type_annotations.
    def enterType_annotations(self, ctx: thriftParser.Type_annotationsContext):
        pass

    # Exit a parse tree produced by thriftParser#type_annotations.
    def exitType_annotations(self, ctx: thriftParser.Type_annotationsContext):
        pass

    # Enter a parse tree produced by thriftParser#type_annotation.
    def enterType_annotation(self, ctx: thriftParser.Type_annotationContext):
        pass

    # Exit a parse tree produced by thriftParser#type_annotation.
    def exitType_annotation(self, ctx: thriftParser.Type_annotationContext):
        pass

    # Enter a parse tree produced by thriftParser#annotation_value.
    def enterAnnotation_value(self, ctx: thriftParser.Annotation_valueContext):
        pass

    # Exit a parse tree produced by thriftParser#annotation_value.
    def exitAnnotation_value(self, ctx: thriftParser.Annotation_valueContext):
        pass

    # Enter a parse tree produced by thriftParser#field_type.
    def enterField_type(self, ctx: thriftParser.Field_typeContext):
        pass

    # Exit a parse tree produced by thriftParser#field_type.
    def exitField_type(self, ctx: thriftParser.Field_typeContext):
        pass

    # Enter a parse tree produced by thriftParser#base_type.
    def enterBase_type(self, ctx: thriftParser.Base_typeContext):
        pass

    # Exit a parse tree produced by thriftParser#base_type.
    def exitBase_type(self, ctx: thriftParser.Base_typeContext):
        pass

    # Enter a parse tree produced by thriftParser#container_type.
    def enterContainer_type(self, ctx: thriftParser.Container_typeContext):
        pass

    # Exit a parse tree produced by thriftParser#container_type.
    def exitContainer_type(self, ctx: thriftParser.Container_typeContext):
        pass

    # Enter a parse tree produced by thriftParser#map_type.
    def enterMap_type(self, ctx: thriftParser.Map_typeContext):
        pass

    # Exit a parse tree produced by thriftParser#map_type.
    def exitMap_type(self, ctx: thriftParser.Map_typeContext):
        pass

    # Enter a parse tree produced by thriftParser#set_type.
    def enterSet_type(self, ctx: thriftParser.Set_typeContext):
        pass

    # Exit a parse tree produced by thriftParser#set_type.
    def exitSet_type(self, ctx: thriftParser.Set_typeContext):
        pass

    # Enter a parse tree produced by thriftParser#list_type.
    def enterList_type(self, ctx: thriftParser.List_typeContext):
        pass

    # Exit a parse tree produced by thriftParser#list_type.
    def exitList_type(self, ctx: thriftParser.List_typeContext):
        pass

    # Enter a parse tree produced by thriftParser#cpp_type.
    def enterCpp_type(self, ctx: thriftParser.Cpp_typeContext):
        pass

    # Exit a parse tree produced by thriftParser#cpp_type.
    def exitCpp_type(self, ctx: thriftParser.Cpp_typeContext):
        pass

    # Enter a parse tree produced by thriftParser#const_value.
    def enterConst_value(self, ctx: thriftParser.Const_valueContext):
        pass

    # Exit a parse tree produced by thriftParser#const_value.
    def exitConst_value(self, ctx: thriftParser.Const_valueContext):
        pass

    # Enter a parse tree produced by thriftParser#integer.
    def enterInteger(self, ctx: thriftParser.IntegerContext):
        pass

    # Exit a parse tree produced by thriftParser#integer.
    def exitInteger(self, ctx: thriftParser.IntegerContext):
        pass

    # Enter a parse tree produced by thriftParser#const_list.
    def enterConst_list(self, ctx: thriftParser.Const_listContext):
        pass

    # Exit a parse tree produced by thriftParser#const_list.
    def exitConst_list(self, ctx: thriftParser.Const_listContext):
        pass

    # Enter a parse tree produced by thriftParser#const_map_entry.
    def enterConst_map_entry(self, ctx: thriftParser.Const_map_entryContext):
        pass

    # Exit a parse tree produced by thriftParser#const_map_entry.
    def exitConst_map_entry(self, ctx: thriftParser.Const_map_entryContext):
        pass

    # Enter a parse tree produced by thriftParser#const_map.
    def enterConst_map(self, ctx: thriftParser.Const_mapContext):
        pass

    # Exit a parse tree produced by thriftParser#const_map.
    def exitConst_map(self, ctx: thriftParser.Const_mapContext):
        pass

    # Enter a parse tree produced by thriftParser#list_separator.
    def enterList_separator(self, ctx: thriftParser.List_separatorContext):
        pass

    # Exit a parse tree produced by thriftParser#list_separator.
    def exitList_separator(self, ctx: thriftParser.List_separatorContext):
        pass

    # Enter a parse tree produced by thriftParser#real_base_type.
    def enterReal_base_type(self, ctx: thriftParser.Real_base_typeContext):
        pass

    # Exit a parse tree produced by thriftParser#real_base_type.
    def exitReal_base_type(self, ctx: thriftParser.Real_base_typeContext):
        pass
