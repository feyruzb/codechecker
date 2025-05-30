<template>
  <v-container fluid class="pa-0">
    <analysis-info-dialog
      :value.sync="analysisInfoDialog"
      :report-id="reportId"
    />

    <v-row class="ma-0">
      <v-col
        class="py-0"
        :cols="editorCols"
      >
        <v-container fluid class="pa-0 mb-2">
          <v-row class="ma-0">
            <v-col
              cols="auto"
              class="pa-0 mr-2"
              align-self="center"
            >
              <show-report-info-dialog :value="report">
                <template v-slot="{ on }">
                  <report-info-button :on="on" />
                </template>
              </show-report-info-dialog>
            </v-col>

            <v-col
              cols="auto"
              class="pa-0 mr-2"
              align-self="center"
            >
              <analysis-info-btn
                @click.native="openAnalysisInfoDialog"
              />
            </v-col>

            <v-col
              cols="auto"
              class="pa-0 mr-2"
              align-self="center"
            >
              <set-cleanup-plan-btn
                :value="report ? [report] : []"
              />
            </v-col>

            <v-col
              cols="auto"
              class="review-status-wrapper pa-0"
              align-self="center"
            >
              <v-container fluid class="pa-0">
                <v-row class="px-4">
                  <v-col cols="auto" class="pa-0">
                    <select-review-status
                      class="mx-0"
                      :value="reviewData"
                      :report="report"
                      :on-confirm="confirmReviewStatusChange"
                    />
                  </v-col>

                  <v-col cols="auto" class="pa-0">
                    <v-menu
                      v-if="reviewData.comment"
                      content-class="review-status-message-dialog"
                      :close-on-content-click="false"
                      :nudge-width="200"
                      offset-x
                    >
                      <template v-slot:activator="{ on }">
                        <v-btn class="review-status-message" icon v-on="on">
                          <v-icon>mdi-message-text-outline</v-icon>
                        </v-btn>
                      </template>
                      <v-card>
                        <v-list>
                          <v-list-item>
                            <v-list-item-avatar>
                              <user-icon :value="reviewData.author" />
                            </v-list-item-avatar>

                            <v-list-item-content>
                              <v-list-item-title>
                                {{ reviewData.author }}
                              </v-list-item-title>
                              <v-list-item-subtitle>
                                {{ reviewData.date | prettifyDate }}
                              </v-list-item-subtitle>
                            </v-list-item-content>
                          </v-list-item>
                        </v-list>

                        <v-divider />

                        <v-list>
                          <v-list-item>
                            <v-list-item-title>
                              {{ reviewData.comment }}
                            </v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-card>
                    </v-menu>
                  </v-col>
                </v-row>
              </v-container>
            </v-col>

            <v-col
              cols="auto"
              class="pa-0"
              align-self="center"
            >
              <v-checkbox
                v-model="showArrows"
                class="show-arrows mx-2 my-0 align-center justify-center"
                label="Show arrows"
                dense
                :hide-details="true"
              />
            </v-col>

            <v-spacer />

            <v-col
              cols="auto"
              class="py-0 pr-0"
              align-self="center"
            >
              <toggle-blame-view-btn
                v-model="enableBlameView"
                :disabled="!hasBlameInfo"
              />
            </v-col>

            <v-col
              cols="auto"
              class="py-0 pr-0"
              align-self="center"
            >
              <v-btn
                class="comments-btn mx-2 mr-0"
                color="primary"
                outlined
                small
                :loading="loadNumOfComments"
                @click="showComments = !showComments"
              >
                <v-icon
                  class="mr-1"
                  small
                >
                  mdi-comment-multiple-outline
                </v-icon>
                Comments ({{ numOfComments }})
              </v-btn>
            </v-col>
          </v-row>
        </v-container>

        <v-container fluid class="pa-0">
          <v-row
            id="editor-wrapper"
            class="ma-0"
          >
            <v-progress-linear
              v-if="loading"
              indeterminate
              class="mb-0"
            />

            <v-col class="pa-0">
              <v-container fluid class="pa-0">
                <v-row
                  class="header pa-1 ma-0"
                  justify="space-between"
                >
                  <v-col
                    v-if="trackingBranch"
                    class="file-path py-0"
                    align-self="center"
                    cols="auto"
                  >
                    <span
                      v-if="sourceFile"
                      :title="`Tracking branch: ${trackingBranch}`"
                      class="grey--text text--darken-3"
                    >
                      <v-icon class="mr-0" small>mdi-source-branch</v-icon>
                      ({{ trackingBranch | truncate(20) }})
                    </span>
                  </v-col>

                  <v-col
                    v-if="trackingBranch"
                    class="py-1 px-0"
                    cols="auto"
                  >
                    <v-divider
                      inset
                      vertical
                      :style="{ display: 'inline' }"
                    />
                  </v-col>

                  <v-col
                    class="file-path py-0 pl-1"
                    align-self="center"
                  >
                    <copy-btn v-if="sourceFile" :value="sourceFile.filePath" />
                    <span
                      v-if="sourceFile"
                      class="file-path"
                      :title="`\u200E${sourceFile.filePath}`"
                    >
                      {{ sourceFile.filePath }}
                    </span>
                  </v-col>

                  <v-col
                    cols="auto"
                    class="py-0"
                    align-self="center"
                  >
                    <v-row
                      align="center"
                      class="text-no-wrap"
                    >
                      Found in:
                      <select-same-report
                        class="select-same-report ml-2"
                        :report="report"
                        @update:report="(reportId) =>
                          $emit('update:report', reportId)"
                      />
                    </v-row>
                  </v-col>
                </v-row>

                <v-row
                  v-fill-height
                  :class="[
                    'editor',
                    'ma-0',
                    enableBlameView ? 'blame' : undefined
                  ]"
                >
                  <textarea ref="editor" />
                </v-row>
              </v-container>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
      <v-col
        v-if="showComments"
        class="pa-0"
        :cols="commentCols"
      >
        <report-comments
          v-fill-height
          class="comments"
          :report="report"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Vue from "vue";

import CodeMirror from "codemirror";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/clike/clike.js";

// Import libaries for code highlights.
import "codemirror/addon/scroll/annotatescrollbar.js";
import "codemirror/addon/search/match-highlighter.js";
import "codemirror/addon/search/matchesonscrollbar.js";

// Import libaries to support code search.
import "codemirror/addon/dialog/dialog.js";
import "codemirror/addon/dialog/dialog.css";
import "codemirror/addon/search/search.js";
import "codemirror/addon/search/searchcursor.js";

import _ from "lodash";

import { jsPlumb } from "jsplumb";

import { format } from "date-fns";

import { ccService, handleThriftError } from "@cc-api";
import {
  Checker,
  Encoding,
  ExtendedReportDataType,
  ReviewData
} from "@cc/report-server-types";

import { FillHeight } from "@/directives";
import { AnalysisInfoDialog, CopyBtn } from "@/components";
import { UserIcon } from "@/components/Icons";

import ReportTreeKind from "@/components/Report/ReportTree/ReportTreeKind";
import { SetCleanupPlanBtn } from "@/components/Report/CleanupPlan";

import AnalysisInfoBtn from "./AnalysisInfoBtn";

import { ReportComments } from "./Comment";
import GitBlameMixin from "./Git/GitBlame";
import ToggleBlameViewBtn from "./Git/ToggleBlameViewBtn";
import SelectReviewStatus from "./SelectReviewStatus";
import SelectSameReport from "./SelectSameReport";
import { ReportInfoButton, ShowReportInfoDialog } from "./ReportInfo";

import ReportStepMessage from "./ReportStepMessage";
const ReportStepMessageClass = Vue.extend(ReportStepMessage);

export default {
  name: "Report",
  components: {
    AnalysisInfoBtn,
    AnalysisInfoDialog,
    CopyBtn,
    ReportComments,
    ReportInfoButton,
    SelectReviewStatus,
    SelectSameReport,
    SetCleanupPlanBtn,
    ShowReportInfoDialog,
    ToggleBlameViewBtn,
    UserIcon
  },
  directives: { FillHeight },
  mixins: [ GitBlameMixin ],
  props: {
    treeItem: { type: Object, default: null }
  },

  emits: [ "update-review-data" ],

  data() {
    const enableBlameView =
      this.$router.currentRoute.query["view"] === "blame";

    return {
      report: null,
      step: null,
      editor: null,
      sourceFile: null,
      jsPlumbInstance: null,
      lineMarks: [],
      lineWidgets: [],
      showArrows: true,
      numOfComments: null,
      loadNumOfComments: true,
      showComments: false,
      commentCols: 3,
      loading: true,
      bus: new Vue(),
      annotation: null,
      selectedChecker: null,
      analysisInfoDialog: false,
      reportId: null,
      enableBlameView,
      docUrl: null
    };
  },

  computed: {
    trackingBranch() {
      return this.sourceFile?.trackingBranch;
    },
    hasBlameInfo() {
      return this.sourceFile?.hasBlameInfo;
    },

    checkerName() {
      return this.report ? this.report.checkerId : null;
    },

    editorCols() {
      const maxCols = 12;

      return this.showComments
        ? maxCols - this.commentCols
        : maxCols;
    },

    reviewData() {
      return this.report && this.report.reviewData
        ? this.report.reviewData
        : new ReviewData();
    }
  },

  watch: {
    async enableBlameView() {
      if (this.enableBlameView) {
        await this.loadBlameView();
      } else {
        await this.hideBlameView();
      }

      // Scroll to the current bug step item.
      this.jumpTo(
        this.treeItem.step?.startLine.toNumber() ||
        this.treeItem.report.line.toNumber());
    },

    treeItem() {
      this.init(this.treeItem);
    },

    showArrows() {
      if (this.showArrows) {
        this.drawBugPath();
      } else {
        this.clearLines();
      }
    },

    report() {
      this.loadNumOfComments = true;
      ccService.getClient().getCommentCount(this.report.reportId,
        handleThriftError(numOfComments => {
          this.numOfComments = numOfComments;
          this.loadNumOfComments = false;
        }));
    }
  },

  created() {
    document.addEventListener("keydown", this.findText);
    window.addEventListener("resize", this.onResize);
  },

  destroyed() {
    document.removeEventListener("keydown", this.findText);
    window.removeEventListener("resize", this.onResize);
  },

  mounted() {
    this.editor = CodeMirror.fromTextArea(this.$refs.editor, {
      lineNumbers: true,
      readOnly: true,
      mode: "text/x-c++src",
      gutters: [ "CodeMirror-linenumbers", "bugInfo" ],
      extraKeys: {},
      viewportMargin: 200,
      highlightSelectionMatches : { showToken: /\w/, annotateScrollbar: true }
    });
    this.editor.setSize("100%", "100%");

    this.editor.on("viewportChange", (cm, from, to) => {
      this.drawLines(from, to);
    });

    this.annotation = this.editor.annotateScrollbar({
      className: "scrollbar-bug-annotation"
    });

    if (this.treeItem) {
      this.init(this.treeItem);
    }

    this.bus.$on("jpmToPrevReport", attrs => {
      this.loadReportStep(this.report, {
        stepId: attrs.$id,
        fileId: attrs.fileId,
        startLine: attrs.startLine
      });
    });

    this.bus.$on("jpmToNextReport", attrs => {
      this.loadReportStep(this.report, {
        stepId: attrs.$id,
        fileId: attrs.fileId,
        startLine: attrs.startLine
      });
    });

    this.bus.$on("showDocumentation", () => {
      this.selectedChecker = new Checker({
        analyzerName: this.report.analyzerName,
        checkerId: this.report.checkerId
      });
    });
  },

  methods: {
    init(treeItem) {
      this.loading = true;

      if (treeItem.step) {
        this.loadReportStep(treeItem.report, {
          stepId: this.treeItem.id,
          ...treeItem.step
        });
      } else if (treeItem.data) {
        this.loadReportStep(treeItem.report, {
          stepId: this.treeItem.id,
          ...treeItem.data
        });
      } else {
        this.loadReport(treeItem.report);
      }
    },

    async loadReportStep(report, { stepId, fileId, startLine }) {
      if (!this.report ||
          !this.report.reportId.equals(report.reportId) ||
          !this.sourceFile ||
          !fileId.equals(this.sourceFile.fileId)
      ) {
        this.report = report;

        await this.setSourceFileData(fileId);
        await this.drawBugPath();
      }

      const line = startLine.toNumber();
      this.jumpTo(line, 0);
      this.updateAnnotation(line);
      this.highlightReportStep(stepId);

      this.loading = false;
    },

    async loadReport(report) {
      if (!report)
        return;

      this.report = report;

      await this.setSourceFileData(report.fileId);
      await this.drawBugPath();

      const line = report.line.toNumber();
      this.jumpTo(line, 0);
      this.updateAnnotation(line);
      this.highlightReport(report);

      this.loading = false;
    },

    updateAnnotation(line) {
      this.annotation.update([ { from: { line }, to: { line } } ]);
    },

    onResize: _.debounce(function () {
      this.annotation.redraw();
    }, 500),

    findText(evt) {
      if (evt.ctrlKey && evt.keyCode === 13) // Enter
        this.editor.execCommand("findPersistentNext");

      if (evt.ctrlKey && evt.keyCode === 70) { // Ctrl-f
        evt.preventDefault();
        evt.stopPropagation();

        this.editor.execCommand("findPersistent");

        // Set focus to the search input field.
        setTimeout(() => {
          const searchField =
            document.getElementsByClassName("CodeMirror-search-field");

          if (searchField.length)
            searchField[0].focus();
        }, 0);
      }
    },

    highlightReportStep(stepId) {
      this.highlightCurrentBubble(stepId);
    },

    highlightReport() {
      this.lineWidgets.forEach(widget => {
        const type = widget.node.getAttribute("type");
        widget.node.classList.toggle("current", type === "error");
      });
    },

    highlightCurrentBubble(id) {
      this.lineWidgets.forEach(widget => {
        const stepId = widget.node.getAttribute("step-id");
        widget.node.classList.toggle("current", stepId === id);
      });
    },

    async setSourceFileData(fileId) {
      const sourceFile = await new Promise(resolve => {
        ccService.getClient().getSourceFileData(fileId, true,
          Encoding.DEFAULT, handleThriftError(sourceFile => {
            resolve(sourceFile);
          }));
      });

      this.sourceFile = sourceFile;
      this.editor.setValue(sourceFile.fileContent);

      if (this.enableBlameView) {
        this.loadBlameView();
      }
    },

    resetJsPlumb() {
      if (this.jsPlumbInstance) {
        this.jsPlumbInstance.reset();
      }

      const jsPlumbParentElement =
        this.$el.querySelector(".CodeMirror-lines");
      jsPlumbParentElement.style.position = "relative";

      this.jsPlumbInstance = jsPlumb.getInstance({
        Container : jsPlumbParentElement,
        Anchor : [ "Perimeter", { shape : "Ellipse" } ],
        Endpoint : [ "Dot", { radius: 1 } ],
        PaintStyle : { stroke : "#a94442", strokeWidth: 2 },
        Connector: [ "Bezier", { curviness: 10 } ],
        ConnectionsDetachable : false,
        ConnectionOverlays : [
          [ "Arrow", { location: 1, length: 10, width: 8 } ]
        ]
      });
    },

    isSameFile (filePath) {
      return filePath.fileId === this.sourceFile.fileId;
    },

    async drawBugPath() {
      this.clearBubbles();
      this.clearLines();

      const reportId = this.report.reportId;
      const reportDetail = await new Promise(resolve => {
        ccService.getClient().getReportDetails(reportId,
          handleThriftError(reportDetail => {
            resolve(reportDetail);
          }));
      });

      const errorChecker = new Checker({
        analyzerName: this.report.analyzerName,
        checkerId: this.report.checkerId
      });
      await new Promise(resolve => {
        ccService.getClient().getCheckerLabels(
          [ errorChecker ],
          handleThriftError(labels => {
            const docUrlLabels = labels[0].filter(
              param => param.startsWith("doc_url")
            );
            this.docUrl = docUrlLabels.length ?
              docUrlLabels[0].split("doc_url:")[1] : null;
            resolve(this.docUrl);
          })
        );
      });

      const isSameFile = path => path.fileId.equals(this.sourceFile.fileId);

      // Add extra path events (macro expansions, notes).
      const extendedData = reportDetail.extendedData.map((data, index) => {
        let kind = null;
        switch (data.type) {
        case ExtendedReportDataType.NOTE:
          kind = ReportTreeKind.NOTE_ITEM;
          break;
        case ExtendedReportDataType.MACRO:
          kind = ReportTreeKind.MACRO_EXPANSION_ITEM;
          break;
        default:
          console.warn("Unhandled extended data type", data.type);
        }

        const id = ReportTreeKind.getId(kind, this.report, index);
        return { ...data, $id: id, $message: data.message };
      }).filter(isSameFile);

      this.addExtendedData(extendedData);

      // Add file path events.
      let prevStep = null;
      const events = reportDetail.pathEvents.map((event, index) => {
        const id = ReportTreeKind.getId(ReportTreeKind.REPORT_STEPS,
          this.report, index);

        const currentStep = {
          ...event,
          $id: id,
          $message: event.msg,
          $index: index + 1,
          $isResult: index === reportDetail.pathEvents.length - 1,
          $prevStep: prevStep
        };

        if (prevStep) {
          prevStep.$nextStep = currentStep;
        }
        prevStep = currentStep;

        return currentStep;
      }).filter(isSameFile);

      this.addEvents(events);

      // Add lines.
      if (this.showArrows) {
        const points = reportDetail.executionPath.filter(isSameFile);
        this.addLines(points);
      }
    },

    clearBubbles() {
      this.editor.operation(() => {
        this.lineWidgets.forEach(widget => widget.clear());
      });

      this.lineWidgets = [];
    },

    clearLines() {
      this.editor.operation(() => {
        this.lineMarks.forEach(mark => mark.clear());
      });

      this.lineMarks = [];
      this.resetJsPlumb();
    },

    addLineWidget(element, props) {
      const marginLeft =
        this.editor.defaultCharWidth() * element.startCol + "px";

      const widget = new ReportStepMessageClass({
        propsData: {
          ...props,
          id: element.$id,
          value: element.$message,
          marginLeft: marginLeft,
          report: this.report
        }
      });
      widget.$vuetify = this.$vuetify;
      widget.$mount();

      this.lineWidgets.push(this.editor.addLineWidget(
        element.startLine.toNumber() - 1, widget.$el));
    },

    renderMainWarning(events) {
      if (!this.sourceFile.fileId.equals(this.report.fileId)) {
        return false;
      }

      if (events.length == 0) {
        return true;
      }

      const lastEvent = events[events.length - 1];
      if (this.report.checkerMsg !== lastEvent.msg ||
        this.report.line.toNumber() != lastEvent.startLine.toNumber()) {
        return true;
      }

      return false;
    },

    addEvents(events) {
      this.editor.operation(() => {
        events.forEach(event => {
          let type = "info";
          if (event.$isResult) {
            type = this.renderMainWarning(events) ? "info" : "error";
          } else if (event.msg.indexOf(" (fixit)") > -1) {
            type = "fixit";
          }

          const props = {
            type: type,
            index: event.$index,
            bus: this.bus,
            prevStep: event.$prevStep,
            nextStep: event.$nextStep,
            docUrl: this.docUrl
          };
          this.addLineWidget(event, props);
        });
      });


      //If the warning message or location is different than the
      //the last bug path element, then we render the warning.
      if (this.renderMainWarning(events)) {
        const chkrmsg_data = { $id: 999,
          $message:this.report.checkerMsg,
          startLine:this.report.line, startCol:this.report.column };
        const chrkmsg_props = { type: "error", index:"E", hideDocUrl:true };
        this.addLineWidget(chkrmsg_data, chrkmsg_props);
      }

    },

    addExtendedData(extendedData) {
      this.editor.operation(() => {
        extendedData.forEach(data => {
          let type = null;
          let value = null;
          switch (data.type) {
          case ExtendedReportDataType.NOTE:
            type = "note";
            value = "Note";
            break;
          case ExtendedReportDataType.MACRO:
            type = "macro";
            value = "Macro Expansion";
            break;
          default:
            console.warn("Unhandled extended data type", data.type);
          }

          const props = { type: type, index: value };
          this.addLineWidget(data, props);
        });
      });
    },

    addLines(points) {
      this.editor.operation(() => {
        points.forEach(p => {
          const from = { line : p.startLine - 1, ch : p.startCol - 1 };
          const to =   { line : p.endLine - 1,   ch : p.endCol.toNumber() };
          const markerId = [ from.line, from.ch, to.line, to.ch ].join("_");

          const opts = {
            className: "checker-step",
            attributes: {
              markerid: markerId
            }
          };

          this.lineMarks.push(this.editor.getDoc().markText(from, to, opts));
        });
      });

      const range = this.editor.getViewport();
      this.drawLines(range.from, range.to);
    },

    drawLines(from, to) {
      if (!this.lineMarks.length) {
        return;
      }

      this.resetJsPlumb();

      let prev = null;
      this.lineMarks
        .filter(textMarker => {
          let line = null;

          // If not in viewport.
          try {
            line = textMarker.lines[0].lineNo();
          } catch (ex) {
            return false;
          }

          if (line < from || line >= to) {
            return false;
          }

          return true;
        })
        .forEach(textMarker => {
          const current = this.getDomToMarker(textMarker);

          if (!current) {
            return;
          }

          if (prev) {
            this.jsPlumbInstance.connect({
              source : prev,
              target : current
            });
          }

          prev = current;
        });
    },

    getDomToMarker(textMarker) {
      const selector = `[markerid='${textMarker.attributes.markerid}']`;
      return this.$el.querySelector(selector);
    },

    jumpTo(line, column) {
      this.editor.scrollIntoView({
        line: line,
        ch: column
      }, 150);
    },

    confirmReviewStatusChange(comment, status, author) {
      ccService.getClient().addReviewStatusRule(this.report.bugHash,
        status, comment, handleThriftError(() => {
          this.reviewData.comment = comment;
          this.reviewData.status = status;
          this.reviewData.author = author;
          this.reviewData.date = format(new Date(), "yyyy-MM-dd HH:mm:ss");
          this.$emit(
            "update-review-data",
            this.reviewData,
            this.report.reportId
          );
        }));
    },

    openAnalysisInfoDialog() {
      this.reportId = this.report.reportId;
      this.analysisInfoDialog = true;
    }
  }
};
</script>

<style lang="scss">
.scrollbar-bug-annotation {
  background-color: red;
}
</style>

<style lang="scss" scoped>
#editor-wrapper {
  border: 1px solid #d8dbe0;

  .header {
    background-color: "#f7f7f7";

    .file-path {
      font-family: monospace;
      color: var(--v-grey-darken4);

      max-width: 100%;
      display: inline-block;
      text-align: left;
      vertical-align: middle;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      direction: rtl;

      &::before {
        content: '\200e';
      }
    }
  }

  .editor {
    font-size: initial;
    line-height: initial;

    ::v-deep .CodeMirror-code > div:hover {
      background-color: lighten(grey, 42%);
    }

    &.blame ::v-deep .CodeMirror {
      line-height: 21px;

      .CodeMirror-gutter-wrapper {
        &, div, span {
          height: 100%;
        }
      }
    }

    ::v-deep .cm-matchhighlight:not(.cm-searching) {
      background-color: lightgreen;
    }

    ::v-deep .CodeMirror-selection-highlight-scrollbar {
      background-color: green;
    }
  }
}

::v-deep .checker-step {
  background-color: #eeb;
}

::v-deep .blame-gutter {
  width: 400px;
  background-color: #f7f7f7;
}

::v-deep .report-step-msg.current {
  border: 2px dashed var(--v-primary-base) !important;
  opacity: 1;
  font-weight: bold;
}

::v-deep .report-step-msg {
  opacity: 0.7;
  font-weight: lighter;
}
</style>