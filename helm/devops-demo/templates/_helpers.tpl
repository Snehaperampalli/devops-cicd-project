{{/* Every resource is named after the Helm release. */}}
{{- define "devops-demo.fullname" -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Labels used by the Service and Deployment to find the pods. */}}
{{- define "devops-demo.selectorLabels" -}}
app.kubernetes.io/name: devops-demo
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/* Labels put on every resource. */}}
{{- define "devops-demo.labels" -}}
{{ include "devops-demo.selectorLabels" . }}
app.kubernetes.io/version: {{ .Values.image.tag | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}
