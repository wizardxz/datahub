# Generated from thrift.g4 by ANTLR 4.7.2
from antlr4 import *

if __name__ is not None and "." in __name__:
    from .thriftParser import thriftParser
else:
    from thriftParser import thriftParser

# This class defines a complete generic visitor for a parse tree produced by thriftParser.


class thriftVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by thriftParser#document.
    def visitDocument(self, ctx: thriftParser.DocumentContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#header.
    def visitHeader(self, ctx: thriftParser.HeaderContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#include_.
    def visitInclude_(self, ctx: thriftParser.Include_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#namespace_.
    def visitNamespace_(self, ctx: thriftParser.Namespace_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#cpp_include.
    def visitCpp_include(self, ctx: thriftParser.Cpp_includeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#definition.
    def visitDefinition(self, ctx: thriftParser.DefinitionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#const_rule.
    def visitConst_rule(self, ctx: thriftParser.Const_ruleContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#typedef_.
    def visitTypedef_(self, ctx: thriftParser.Typedef_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#enum_rule.
    def visitEnum_rule(self, ctx: thriftParser.Enum_ruleContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#enum_field.
    def visitEnum_field(self, ctx: thriftParser.Enum_fieldContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#senum.
    def visitSenum(self, ctx: thriftParser.SenumContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#struct_.
    def visitStruct_(self, ctx: thriftParser.Struct_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#union_.
    def visitUnion_(self, ctx: thriftParser.Union_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#exception.
    def visitException(self, ctx: thriftParser.ExceptionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#service.
    def visitService(self, ctx: thriftParser.ServiceContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#field.
    def visitField(self, ctx: thriftParser.FieldContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#field_id.
    def visitField_id(self, ctx: thriftParser.Field_idContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#field_req.
    def visitField_req(self, ctx: thriftParser.Field_reqContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#function_.
    def visitFunction_(self, ctx: thriftParser.Function_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#oneway.
    def visitOneway(self, ctx: thriftParser.OnewayContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#function_type.
    def visitFunction_type(self, ctx: thriftParser.Function_typeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#throws_list.
    def visitThrows_list(self, ctx: thriftParser.Throws_listContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#type_annotations.
    def visitType_annotations(self, ctx: thriftParser.Type_annotationsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#type_annotation.
    def visitType_annotation(self, ctx: thriftParser.Type_annotationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#annotation_value.
    def visitAnnotation_value(self, ctx: thriftParser.Annotation_valueContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#field_type.
    def visitField_type(self, ctx: thriftParser.Field_typeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#base_type.
    def visitBase_type(self, ctx: thriftParser.Base_typeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#container_type.
    def visitContainer_type(self, ctx: thriftParser.Container_typeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#map_type.
    def visitMap_type(self, ctx: thriftParser.Map_typeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#set_type.
    def visitSet_type(self, ctx: thriftParser.Set_typeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#list_type.
    def visitList_type(self, ctx: thriftParser.List_typeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#cpp_type.
    def visitCpp_type(self, ctx: thriftParser.Cpp_typeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#const_value.
    def visitConst_value(self, ctx: thriftParser.Const_valueContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#integer.
    def visitInteger(self, ctx: thriftParser.IntegerContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#const_list.
    def visitConst_list(self, ctx: thriftParser.Const_listContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#const_map_entry.
    def visitConst_map_entry(self, ctx: thriftParser.Const_map_entryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#const_map.
    def visitConst_map(self, ctx: thriftParser.Const_mapContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#list_separator.
    def visitList_separator(self, ctx: thriftParser.List_separatorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by thriftParser#real_base_type.
    def visitReal_base_type(self, ctx: thriftParser.Real_base_typeContext):
        return self.visitChildren(ctx)


del thriftParser
