{{/* Base name for every resource: the release name, or "<release>-stockpilot". */}}
{{- define "stockpilot.fullname" -}}
{{- if contains "stockpilot" .Release.Name -}}
{{- .Release.Name | trunc 50 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-stockpilot" .Release.Name | trunc 50 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{/* Common labels. Usage: include "stockpilot.labels" (dict "root" $ "component" "backend") */}}
{{- define "stockpilot.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .root.Chart.Name .root.Chart.Version }}
app.kubernetes.io/managed-by: {{ .root.Release.Service }}
app.kubernetes.io/part-of: stockpilot
app.kubernetes.io/version: {{ .root.Values.imageTag | trunc 63 | quote }}
{{ include "stockpilot.selectorLabels" . }}
{{- end -}}

{{/* Labels used by selectors. These must never change between releases. */}}
{{- define "stockpilot.selectorLabels" -}}
app.kubernetes.io/name: stockpilot
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}

{{/* Image reference. Usage: include "stockpilot.image" (dict "root" $ "component" "backend") */}}
{{- define "stockpilot.image" -}}
{{- printf "%s/stockpilot-%s:%s" .root.Values.imageRegistry .component .root.Values.imageTag -}}
{{- end -}}

{{/* Pod-level security context shared by app pods (meets the "restricted" Pod Security Standard). */}}
{{- define "stockpilot.podSecurityContext" -}}
runAsNonRoot: true
runAsUser: {{ .uid }}
runAsGroup: {{ .uid }}
seccompProfile:
  type: RuntimeDefault
{{- end -}}

{{- define "stockpilot.containerSecurityContext" -}}
allowPrivilegeEscalation: false
capabilities:
  drop: ["ALL"]
{{- end -}}
